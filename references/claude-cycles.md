# Claude’s Cycles (pdftotext extraction)

Source PDF: `claude-cycles.pdf`
Extraction: `pdftotext -layout` (page-by-page)

## Page 1

```text
                                               Claude’s Cycles
                            Don Knuth, Stanford Computer Science Department
                                (28 February 2026; revised 02 March 2026)
Shock! Shock! I learned yesterday that an open problem I’d been working on for several weeks had just
been solved by Claude Opus 4.6 — Anthropic’s hybrid reasoning model that had been released three weeks
earlier! It seems that I’ll have to revise my opinions about “generative AI” one of these days. What a joy
it is to learn not only that my conjecture has a nice solution but also to celebrate this dramatic advance in
automatic deduction and creative problem solving. I’ll try to tell the story brieﬂy in this note.
      Here’s the problem, which came up while I was writing about directed Hamiltonian cycles for a future
volume of The Art of Computer Programming:
           Consider the digraph with m3 vertices ijk for 0 ≤ i, j, k < m, and three arcs from
           each vertex, namely to i+jk, ij +k, and ijk+ , where i+ = (i +1) mod m. Try to ﬁnd
           a general decomposition of the arcs into three directed m3 -cycles, for all m > 2.
I had solved the problem for m = 3, and asked for a generalization as part of the answer to an exercise in
[3]. My friend Filip Stappers rose to the challenge, and empirically discovered solutions for 4 ≤ m ≤ 16;
therefore it became highly likely that the desired decompositions do exist, except when m ≤ 2.
     Indeed, it was Filip who had the gumption to pose this question to Claude, using exactly the wording
above. He also gave guidance/coaching, instructing Claude to summarize its ongoing progress:
             ** After EVERY exploreXX.py run, IMMEDIATELY update this ﬁle [plan.md]
             before doing anything else. ** No exceptions. Do not start the next exploration
             until the previous one is documented here.
And Claude’s plan of attack was quite admirable. First it reformulated the problem: “Need sigma: Zm3 → S3 ,
assigning a permutation of {0, 1, 2} at each vertex; cycle c at vertex v goes in direction sigma(v)[c]. Each
resulting functional digraph must be a single Hamiltonian cycle.” Then it tried for a simple answer: “‘If
sigma is cyclic, i.e. fc(v) = (c + g(v)) mod 3 for some g : Zm3 → Z3 , then we only need one function g. Tested
linear g = (a · i + b · j + c · k) mod 3 and quadratic variants. No linear or simple quadratic g works.”
     Claude’s second exploration was what it called a DFS search attempt (depth-ﬁrst search): “Attempted
brute-force DFS over sigma assignments for m = 3 (627 search space). Too slow without good pruning.”
     Thirdly, it tried what it called 2D serpentine analysis: “Key 2D result: The pattern [0m 1 1]m gives a
                                                                                                   −


Hamiltonian cycle in Cay(Zm2 , {e0, e1 }) for m = 3. Its complement also works, giving a valid 2D decomposi-
tion.” This is really impressive! First Claude recognized the digraph as a so-called Cayley digraph with two
generators, traditionally called e0 and e1 ; a mathematician will understand that the arcs act as a group on
m2 vertices, where e0 increments the ﬁrst component while e1 increments the second. Then it formulated
the cycle symbolically for general m, although for some reason it still said that it was only looking at m = 3.
And it decided to call this a “serpentine pattern”!
     Exploration number 4 constructed the “3D serpentine pattern” [0m 1 1]m 1 [0m 12]m . (That’s a typo-
                                                                            −      −     −


graphic error for [[0m 11]m 1 0m 1 2]m. It’s a classical sequence called the “modular m-ary Gray code” on
                      −      −    −


page 299 of [2].) After deleting this cycle from the graph, Claude looked at the remaining 2-regular digraph
and found that it has “rigid structure making decomposition diﬃcult.”
     Nevertheless, exploration number 5 analyzed that residual digraph, ﬁnding some cycles. Unfortunately
they didn’t work out.
     Back to the drawing board. Several other approaches were tried, for example looking at the choices
to be made at vertices that lie on the hyperplane where i + j + k is congruent to −1. Nothing promising
showed up until exploration number 15, which introduced what Claude called a ﬁber decomposition : “The
quotient map ?(i, j, k) = i + j + k mod m maps all arcs from ﬁber Fs to Fs+1 . The digraph is layered. In ﬁber
coordinates (i, j ) with k = (s − i − j ) mod m.”
     Using those ﬁber coordinates, the problem could now be reformulated as choosing, for each (i, j, s), a
permutation of the three operators that shift (i, j ) by either (1, 0) or (0, 1) or (0, 0). “Tried sigma depending
                                                        1
```

## Page 2

```text
only on ﬁber index s (rotation by s): gives the (i + j + k) mod 3 pattern which doesn’t work. Random local
search found solutions for m = 3 but no general pattern emerged.”
     Exploration 18 “implemented the full ﬁber framework as executable code. Exhaustive backtracking for
m = 3 found a valid decomposition in 0.1s (10932 nodes).” In this solution the permutation sigma was the
same for all (i, j ) in ﬁber s = 0. A similarly “uniform” ﬁber was found for m = 4 by simulated annealing, as
part of exploration 20.
     In exploration 21, Claude realized that the 2D serpentine function “Q(i, j ) = (i +1, j ) if i + j = m − 1
mod m, else (i, j +1)” had nice properties. It looked promising when a uniform choice is made at ﬁber 0 and
a version of the serpentine at all other ﬁbers, if and only if m is odd.
     That triggered a bunch of experiments with simulated annealing “at scale”; but all was for naught. The
conclusion after exploration 25 was “SA can ﬁnd solutions but cannot give a general construction. Need
pure math.”
     So now Claude put on a new thinking cap. At one point it said to itself, “Maybe the right framing is:
don’t think in ﬁbers, think directly about what makes a Hamiltonian cycle.”
     There was a near miss at exploration number 27. “Take the 3D serpentine for cycle 0, apply cyclic
coordinate rotation to get cycles 1 and 2: d1 (i, j, k) = (d0 (j, k, i)+1) mod 3; d2 (i, j, k) = (d0 (k, i, j )+
2) mod 3; all three are individually Hamiltonian for every m = 3 . . 9 tested! Only 3(m − 1) out of m3 vertices
have conﬂicts. all lie on the hyperplane i + j + k = m − 1 mod m.”
     Unfortunately, those conﬂicts couldn’t be resolved. Exploration 29 proved that many plausible scenarios
were in fact impossible. “This kills the ‘single-hyperplane + rotation’ approach entirely. . . . We must allow
the direction function to use diﬀerent values across a rotation orbit.”
     But, aha. Exploration 30 went back to the solution found by SA in exploration 20 and noticed that
the choice at each ﬁber depends on only a single coordinate: s = 0 only on j ; s = 1 and s = 2 only on i.
This led to a concrete construction (exploration 31), in the form of a Python program, which produced valid
results for m = 3, 5, 7, 9, and 11 — hooray! “All three cycles are Hamiltonian, all arcs are used, perfect
decomposition!”
     Here is a simpliﬁcation of that Python program, converted into C form:
                            int c, i, j, k, m, s, t;
                            char ∗d;
                            for (c = 0; c < 3; c++) {
                              for (t = i = j = k = 0; ; t++) {
                                 printf ("%x%x%x ", i, j, k);
                                 if (t == m ∗ m ∗ m) break;
                                 s = (i + j + k) % m;
                                 if (s == 0) d = (j == m − 1? "012" : "210";
                                 else if (s == m − 1) d = (i > 0? "120" : "210";
                                 else d = (i == m − 1? "201" : "102");
                                 switch (d [c]) {
                            case ’0’: i = (i +1) % m; break;
                            case ’1’: j = (j +1) % m; break;
                            case ’2’: k = (k +1) % m; break;
                                 }
                              }
                              printf ("\n");
                            }
     Filip Stappers tested Claude’s Python program for all odd m between 3 and 101, ﬁnding perfect de-
compositions each time. Thus he concluded, quite reasonably, that the problem was indeed solved for odd
values of m. And he quickly sent me the shocking news.
     Of course, a rigorous proof was still needed. And the construction of such a proof turns out to be quite
interesting. Let’s look, for example, at the ﬁrst cycle that is printed; we must prove that it has length m3 .
                                                       2
```

## Page 3

```text
The rule for that cycle is nontrivial, yet fairly simple: Let s = (i + j + k) mod m.
                               When s = 0, bump i if j = m − 1, otherwise bump k.
                        When 0 < s < m − 1, bump k if i = m − 1, otherwise bump j .
                           When s = m − 1, bump j if i > 0, otherwise bump k.
(“Bump” means “increase by 1, mod m.”) Hence in the special case m = 3 that cycle is

                  022 −−→ 002 −−→ 000 −−→ 001 −−→ 011 −−→ 012 −−→ 010 −−→ 020 −−→ 021 −−→
                  121 −−→ 101 −−→ 111 −−→ 112 −−→ 122 −−→ 102 −−→ 100 −−→ 110 −−→ 120 −−→
                  220 −−→ 221 −−→ 201 −−→ 202 −−→ 200 −−→ 210 −−→ 211 −−→ 212 −−→ 222 −−→ 022.

And in the special case m = 5 it’s

       042 −−→ 002 −−→ 012 −−→ 022 −−→ 023 −−→ 024 −−→ 034 −−→ 044 −−→ 004 −−→ 000 −−→ 001 −−→ 011 −−→ 021 −−→
           031 −−→ 032 −−→ 033 −−→ 043 −−→ 003 −−→ 013 −−→ 014 −−→ 010 −−→ 020 −−→ 030 −−→ 040 −−→ 041 −−→
       141 −−→ 101 −−→ 111 −−→ 121 −−→ 131 −−→ 132 −−→ 142 −−→ 102 −−→ 112 −−→ 122 −−→ 123 −−→ 133 −−→ 143 −−→
           103 −−→ 113 −−→ 114 −−→ 124 −−→ 134 −−→ 144 −−→ 104 −−→ 100 −−→ 110 −−→ 120 −−→ 130 −−→ 140 −−→
       240 −−→ 200 −−→ 210 −−→ 220 −−→ 230 −−→ 231 −−→ 241 −−→ 201 −−→ 211 −−→ 221 −−→ 222 −−→ 232 −−→ 242 −−→
           202 −−→ 212 −−→ 213 −−→ 223 −−→ 233 −−→ 243 −−→ 203 −−→ 204 −−→ 214 −−→ 224 −−→ 234 −−→ 244 −−→
       344 −−→ 304 −−→ 314 −−→ 324 −−→ 334 −−→ 330 −−→ 340 −−→ 300 −−→ 310 −−→ 320 −−→ 321 −−→ 331 −−→ 341 −−→
           301 −−→ 311 −−→ 312 −−→ 322 −−→ 332 −−→ 342 −−→ 302 −−→ 303 −−→ 313 −−→ 323 −−→ 333 −−→ 343 −−→
       443 −−→ 444 −−→ 440 −−→ 441 −−→ 401 −−→ 402 −−→ 403 −−→ 404 −−→ 400 −−→ 410 −−→ 411 −−→ 412 −−→ 413 −−→
           414 −−→ 424 −−→ 420 −−→ 421 −−→ 422 −−→ 423 −−→ 433 −−→ 434 −−→ 430 −−→ 431 −−→ 432 −−→ 442 −−→ 042.

Triples for the same value of s are spaced exactly m steps apart. To prove that all m3 triples occur, we need
to prove that the m2 triples for any given value of s are all present.
     Notice that the ﬁrst coordinate, i, changes only when s = 0 and j = m − 1. Thus the m2 triples with
any given value of the ﬁrst coordinate i all occur consecutively. (Our example cycles indicate this by starting
at the vertex where i has just changed to 0, instead of starting at vertex 000.)
     Notice that the cycle elements with i = 0 must start in general with the vertex 0(m − 1)2, because the
previous vertex must have had i = j = m − 1 and s = 0. And 0(m − 1)2, which has s = 1, is followed in
general by 002, 012, . . . , 0(m − 3)2, 0(m − 3)3, taking us back to s = 0.
     In general 0(m − k)k is immediately followed by 0(m − k)(k +1) when 1 < k < m; and then j increases
until we reach 0(m − k − 2)(k +1), whose successor is 0(m − k − 2)(k +2). Thus k is increased by 2, modulo m,
each time we hit a vertex with s = 0. Since m is odd, we’ll eventually get to 0(m − 1)1 — at which time we
will have seen all m2 vertices of the form 0jk. And the successor of 0(m − 1)1 is 1(m − 1)1.
     So far so good! In general, the cycle elements whose ﬁrst component i satisﬁes 0 < i < m − 1 will start
with i(m − 1)(2 − i), where 2 − i is of course evaluated mod m. If all goes well those elements should include
all m2 vertices that begin with i, ending with i(m − i)(1 − i) — whose successor is (i +1)(m − 1)(1 − i). And
all does go well: We repeatedly advance the second component except when s = 0; hence the vertices that
we see when s = 0 are i(m − 2)(2 − i), i(m − 3)(3 − i), . . . , i0(m − i), i(m − 1)(1 − i).
     Finally we reach (m − 1)(m − 1)3, the ﬁrst vertex for which i = m − 1. The local rules change again:
From now on we’ll repeatedly advance the third component, except when s = m − 1. The vertices we see
when s = 0 are (m − 1)01, (m − 1)10, . . . , (m − 1)(m − 1)2. QED.
     We’ve now proved that the ﬁrst cycle (the cycle for c = 0 in the C program) is Hamiltonian. Similar
proofs can be carried out for the other two cycles. (See the Appendix.)
     For fun, let’s consider a larger class of cycles for which such proofs exist. Indeed, it turns out that there
are hundreds of way to solve the stated decomposition problem for odd m; Claude Opus 4.6 happened to
discover just one of them, by deducing where to look.
                                                         3
```

## Page 4

```text
     We shall say that a Hamiltonian cycle C for m = 3 is generalizable if the following construction yields
a Hamiltonian cycle for all odd m ≥ 3: “Given an arbitrary vertex IJK for 0 ≤ I, J, K < m, let i = I ,                


j = J , s = S , and k = (s − i − j ) mod 3, where S = (I + J + K ) mod m, 0 = 0, (m − 1) = 2, and x = 1 for
                                                                                                          


0 < x < m − 1. Obtain the successor of IJK by bumping the coordinate that cycle C bumps when forming
the successor of ijk.” For example, if m = 5 and IJK = 301, we have i = 1, j = 0, S = 4, s = 2, k = 1. So
the successor of 301 will be either 401 or 311 or 302, depending on whether C contains the arc 101 −−→ 201
or 101 −−→ 111 or 101 −−→ 102.
     Claude’s cycle in the example above for m = 3 is generalizable; indeed, we’ve seen its generalization for
m = 5. But it’s easy to ﬁnd cycles that are not generalizable. For instance, if C is the cycle
  000 −−→ 001 −−→ 002 −−→ 012 −−→ 010 −−→ 011 −−→ 021 −−→ 022 −−→ 020 −−→ 120 −−→ 100 −−→ 101 −−→ 111 −−→ 121 −−→
        122 −−→ 102 −−→ 112 −−→ 110 −−→ 210 −−→ 211 −−→ 212 −−→ 222 −−→ 220 −−→ 221 −−→ 201 −−→ 202 −−→ 200 −−→ 000
(which happens to be the lexicographically smallest of all Hamiltonian cycles for the case m = 3), we get
the following “generalization” for m = 5:
  000 −−→ 001 −−→ 002 −−→ 003 −−→ 004 −−→ 014 −−→ 010 −−→ 011 −−→ 012 −−→ 013 −−→ 023 −−→ 024 −−→ 020 −−→
    021 −−→ 022 −−→ 032 −−→ 033 −−→ 034 −−→ 030 −−→ 031 −−→ 041 −−→ 042 −−→ 043 −−→ 044 −−→ 040 −−→ 140 −−→
    100 −−→ 101 −−→ 102 −−→ 103 −−→ 113 −−→ 123 −−→ 124 −−→ 120 −−→ 121 −−→ 221 −−→ 231 −−→ 232 −−→ 233 −−→
    234 −−→ 334 −−→ 344 −−→ 340 −−→ 341 −−→ 342 −−→ 302 −−→ 312 −−→ 313 −−→ 314 −−→ 310 −−→ 410 −−→ 411 −−→
    412 −−→ 413 −−→ 414 −−→ 424 −−→ 420 −−→ 421 −−→ 422 −−→ 423 −−→ 433 −−→ 434 −−→ 430 −−→ 431 −−→ 432 −−→
    442 −−→ 443 −−→ 444 −−→ 440 −−→ 441 −−→ 401 −−→ 402 −−→ 403 −−→ 404 −−→ 400 −−→ 000 .
Oops — this cycle has length 75, not 125.
     It turns out that there are exactly 11502 Hamiltonian cycles for m = 3, of which exactly 1012 generalize
to Hamiltonian cycles for m = 5. Furthermore, exactly 996 of them generalize to Hamiltonian cycles for
both m = 5 and m = 7. And those 996 are in fact generalizable to all odd m > 1.
     Now here’s the point: Let’s say that a decomposition is “Claude-like” if it can be generated by a C
program like the one above, in which the permutations d of {0, 1, 2} depend only on whether i, j , and s are
0 or m − 1 or not. No special cases other than 0 and m − 1 are allowed to aﬀect the choice of d.
Theorem. A Claude-like decomposition is valid for all odd m > 1 if and only if each of the three sequences
that it deﬁnes for m = 3 is generalizable.
Proof. If those three sequences aren’t Hamiltonian, or if they don’t generalize to Hamiltonian cycles for all
odd m > 1, they certainly don’t deﬁne a valid decomposition. Conversely, if they are Hamiltonian cycles
that generalize to Hamiltonian cycles for all odd m > 1, they certainly are valid: Every vertex ijk appears in
each of the three cycles, and its three outgoing arcs are partitioned properly because d is a permutation.
     By setting up an exact cover problem, using the 11502 Hamiltonian cycles for m = 3, we can deduce
that there are exactly 4554 solutions to the 3 × 3 × 3 decomposition problem. And in a similar fashion, if we
study all ways to cover every arc by using just three of the 996 cycles that are generalizable, we ﬁnd that
exactly 760 of those 4554 solutions involve only generalizable cycles — about one in every 6. Consequently
the theorem tells us that exactly 760 Claude-like decompositions are valid for all odd m > 1.
     Maybe the decomposition that Claude found wasn’t the “nicest” of those 760. Can we do better? I
looked at several of them and found that they have somewhat diﬀerent behaviors. Yet I didn’t encounter
any that were actually nicer.
     The dependence on i, j , and s means that these decompositions don’t have cyclic symmetry. I did
notice, to my surprise, that 136 of the 760 generalizable 3 × 3 × 3 cycles remain generalizable when we map
ijk to jki. However, none are common to all three mappings {ijk, jki, kij }.
     Filip told me that the explorations reported above, though ultimately successful, weren’t really smooth.
He had to do some restarts when Claude stopped on random errors; then some of the previous search results
were lost. After every two or three test programs were run, he had to remind Claude again and again that
it was supposed to document its progress carefully.
     Delicious success for odd m, at exploration number 31, came about one hour after the session began.
                                                         4
```

## Page 5

```text
    This decomposition problem remains open for even values of m. The case m = 2 was proved impossible
long ago [1]. As part of exploration number 24, Claude said that it had found solutions for m = 4, m = 6,
and m = 8; yet it saw no way to generalize those results.
    Filip also told me that he asked Claude to continue on the even case after the odd case had been resolved.
“But there after a while it seemed to get stuck. In the end, it was not even able to write and run explore
programs correctly anymore, very weird. So I stopped the search.”
    All in all, however, this was deﬁnitely an impressive success story. I think Claude Shannon’s spirit is
probably proud to know that his name is now being associated with such advances. Hats oﬀ to Claude!
Appendix. Claude’s second cycle (c = 1) is governed by the following rules: “If s = 0, bump j . If
0 < s < m +1, bump i. If s = m − 1 and i > 0, bump k. If s = m − 1 and i = 0, bump j .”
        We can show that the vertices with s = 0 are seen in the following order, for k = 0, 1, . . . , m − 1:
0k(−k), (−2)(1+ k)(1 − k), (−4)(2+ k)(2 − k), . . . 2(−1+ k)(−1 − k). And that will establish the order in
which vertices with s = 1, 2, . . . , m − 1 are seen.
        Claude’s third cycle (c = 2) is governed by somewhat more complex rules: “If s = 0 and j < m − 1,
bump i. If s = 0 and j = m − 1, bump k. If 0 < s < m − 1 and i < m − 1, bump k. If 0 < s < m − 1 and
i = m − 1, bump j . If s = m − 1, bump i.”
        The vertices with s = 0 and j < m − 1 are seen in the following order: 0j (−j ), 2j (−2 − j ), 4j (−4 − j ), . . . ,
(−2)j (2 − j ). And the successors of the latter vertex are (−1)j (2 − j ), (−1)(j +1)(2 − j ), (−1)(j +2)(2 − j ),
. . . , (−1)(j − 2)(2 − j ), 0(j − 2)(2 − j ).
        But the vertices with s = 0 and j = m − 1 are seen thus: 0(−1)1, 1(−1)0, 2(−1)(−1), . . . , (−1)(−1)2.
And the successors of the latter vertex are (−1)(−1)3, (−1)03, (−1)13, . . . (−1)(−3)3, 0(−3)3.
        Thus in every case the sequence of m vertices for s = 0 and a given j is followed by the sequence for
s = 0 and j − 2, modulo m.
References.
[1] Jacques Aubert and Bernadette Schneider, “Graphes orientes indécomposables en circuits hamiltoniens.”
Journal of Combinatorial Theory B32 (1982), 347–349.
[2] Donald E. Knuth, The Art of Computer Programming, Volume 4A: Combinatorial Algorithms, Part 1
(Upper Saddle River, N. J.: Addison–Wesley, 2011), xvi+883 pp.
[3] Donald E. Knuth, preliminary drafts entitled “Hamiltonian paths and cycles,” currently posted at
https://cs.stanford.edu/~knuth/fasc8a.ps.gz and updated frequently as more material is being ac-
cumulated.




                                                             5
```

