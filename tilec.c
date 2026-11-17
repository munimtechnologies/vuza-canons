/* SPDX-License-Identifier: Apache-2.0
 * tilec: every complement of a finite set in Z_N, by exact-cover search.
 * Part of vuza-canons. Made by MV2 of Munim, Inc., with AI agents.
 * Licensed under the Apache License 2.0.
 *
 * Input (stdin): first line "N time_limit_seconds" (0 = no limit), then one
 *   set per line: "id k a_1 ... a_k".
 * Output (stdout), for each input set:
 *   "C id b_1 ... b_m"  once per translation class of APERIODIC complements B,
 *                       written as its lexicographically least translate that
 *                       contains 0 (sorted ascending, b_1 = 0);
 *   "D id solutions_with_0 classes aperiodic_classes complete nodes seconds"
 *                       a summary line (classes counts periodic ones too).
 *
 * Search: the least uncovered pulse x must be covered by a + r for exactly
 * one a in A, so r = x - a. Every complement containing 0 is reached exactly
 * once. Bit sets of N bits, N <= 2048.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAXN 2048
#define MAXW ((MAXN + 63) / 64)

static int N, NW;
static uint64_t LAST;
static uint64_t tr[MAXN][MAXW];      /* tr[r] = bit set of A + r */
static uint64_t cov[MAXN + 1][MAXW]; /* cov[d] = covered pulses with d elements chosen */
static int A[MAXN], K, M;
static int B[MAXN], SB[MAXN], GP[MAXN];
static unsigned char inB[MAXN];
static int primes[32], NP;
static long long nsol, ncls, naper, nodes;
static long cur_id;
static double tlimit;
static clock_t t0;
static int stopped;

static int cmpint(const void *a, const void *b) {
    int x = *(const int *)a, y = *(const int *)b;
    return (x > y) - (x < y);
}

/* B[0..M-1] is a complement containing 0. Keep it only if it is the least
 * translate of its class (lexicographic order of sorted elements, which is
 * the least rotation of its cyclic gap sequence). */
static void solution(void) {
    int i, j, p, periodic;
    nsol++;
    memcpy(SB, B, (size_t)M * sizeof(int));
    qsort(SB, (size_t)M, sizeof(int), cmpint);
    for (i = 0; i + 1 < M; i++) GP[i] = SB[i + 1] - SB[i];
    GP[M - 1] = N - SB[M - 1];
    for (i = 1; i < M; i++) {
        if (GP[i] < GP[0]) return;
        if (GP[i] == GP[0]) {
            for (j = 1; j < M; j++) {
                int a = GP[(i + j) % M], b = GP[j];
                if (a < b) return;
                if (a > b) break;
            }
        }
    }
    ncls++;
    for (i = 0; i < M; i++) inB[SB[i]] = 1;
    periodic = 0;
    for (p = 0; p < NP && !periodic; p++) {
        int g = N / primes[p], all = 1;
        for (i = 0; i < M; i++) {
            if (!inB[(SB[i] + g) % N]) {
                all = 0;
                break;
            }
        }
        periodic = all;
    }
    for (i = 0; i < M; i++) inB[SB[i]] = 0;
    if (periodic) return;
    naper++;
    printf("C %ld", cur_id);
    for (i = 0; i < M; i++) printf(" %d", SB[i]);
    putchar('\n');
}

static void dfs(int d) {
    int w, i, x;
    const uint64_t *c;
    nodes++;
    if (tlimit > 0 && (nodes & 0xFFFF) == 0) {
        if ((double)(clock() - t0) / CLOCKS_PER_SEC > tlimit) stopped = 1;
    }
    if (stopped) return;
    if (d == M) {
        solution();
        return;
    }
    c = cov[d];
    x = -1;
    for (w = 0; w < NW; w++) {
        uint64_t f = ~c[w];
        if (w == NW - 1) f &= LAST;
        if (f) {
            x = w * 64 + __builtin_ctzll(f);
            break;
        }
    }
    if (x < 0) return;
    for (i = 0; i < K; i++) {
        int r = x - A[i];
        const uint64_t *m;
        uint64_t *nc;
        if (r < 0) r += N;
        m = tr[r];
        for (w = 0; w < NW; w++)
            if (m[w] & c[w]) break;
        if (w < NW) continue;
        nc = cov[d + 1];
        for (w = 0; w < NW; w++) nc[w] = c[w] | m[w];
        B[d] = r;
        dfs(d + 1);
        if (stopped) return;
    }
}

int main(void) {
    int i, w, r, n, d;
    if (scanf("%d %lf", &N, &tlimit) != 2 || N < 2 || N > MAXN) {
        fprintf(stderr, "tilec: bad header (N must be 2..%d)\n", MAXN);
        return 2;
    }
    NW = (N + 63) / 64;
    LAST = (N % 64 == 0) ? ~0ULL : ((1ULL << (N % 64)) - 1ULL);
    n = N;
    NP = 0;
    for (d = 2; d * d <= n; d++) {
        if (n % d == 0) {
            primes[NP++] = d;
            while (n % d == 0) n /= d;
        }
    }
    if (n > 1) primes[NP++] = n;

    while (scanf("%ld %d", &cur_id, &K) == 2) {
        int ok, bits;
        if (K < 1 || K > N) {
            fprintf(stderr, "tilec: bad k\n");
            return 2;
        }
        for (i = 0; i < K; i++) {
            if (scanf("%d", &A[i]) != 1) {
                fprintf(stderr, "tilec: short line\n");
                return 2;
            }
            A[i] %= N;
            if (A[i] < 0) A[i] += N;
        }
        nsol = ncls = naper = nodes = 0;
        stopped = 0;
        t0 = clock();
        ok = (N % K == 0);
        if (ok) {
            M = N / K;
            for (r = 0; r < N; r++) {
                for (w = 0; w < NW; w++) tr[r][w] = 0;
                for (i = 0; i < K; i++) {
                    int x = (A[i] + r) % N;
                    tr[r][x >> 6] |= 1ULL << (x & 63);
                }
            }
            bits = 0;
            for (w = 0; w < NW; w++) bits += __builtin_popcountll(tr[0][w]);
            if (bits != K) ok = 0; /* repeated elements: not a set */
        }
        if (ok) {
            for (w = 0; w < NW; w++) cov[1][w] = tr[0][w];
            B[0] = 0;
            dfs(1);
        }
        printf("D %ld %lld %lld %lld %d %lld %.3f\n", cur_id, nsol, ncls, naper, stopped ? 0 : 1, nodes,
               (double)(clock() - t0) / CLOCKS_PER_SEC);
        fflush(stdout);
    }
    return 0;
}
