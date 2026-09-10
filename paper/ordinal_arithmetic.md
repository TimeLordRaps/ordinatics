# Ordinal Arithmetic: An Ordinal-First Metalanguage Approach to Definable Arithmetic Truth

Tyler Roost

Manuscript draft, September 10, 2026

## Abstract

Ordinatics proposes an arithmetic of ordinal forms with division and a finite-valued wrap map, while retaining distinctions between construction paths and numerical outcomes. We give a bounded mathematical reconstruction directed at the definition of arithmetic truth in an ordinal framework. Finite ordinals supply the arithmetic domain, and ordinals below $\omega^\omega$ index a hierarchy of languages whose truth predicates apply to earlier languages. In an explicit set-theoretic metatheory, the hierarchy has a unique satisfaction interpretation and preserves arithmetic truth under passage to later stages. Each stage nevertheless lacks a definition of its own full truth predicate. We also construct a rational-function value layer with partial specialization $W(X)=-1/2$. To formalize the stronger objective of Gödelian completeness through fractal meta-representations, we specify a ranked self-closing meta-surface in which closed derivations and their acceptance derivations can be reified at successive ranks. We formalize observation-exactness as an information-preservation condition, compare the target with Feferman's completeness theorem for transfinite reflection progressions, and prove a conditional record-coverage theorem whose conclusion quantifies over native records alone. A checked finite calculus retains composed rule trees, encodes records and formulas as single free ground terms, and checks packed numerical representations. One explicit model of all current source clauses preserves those records, while its path relation does not implement their direct transition to conclusions. A full Hypermath-derived ranked realization, arithmetic checker agreement, arithmetic interpretation, and soundness proof remain open. The contribution is an explicit interface, bounded constructions, and proof-obligation analysis; it does not establish arithmetic completeness.

**Keywords:** Ordinatics; ordinal arithmetic; satisfaction; ramified truth; uniform reflection; fractal meta-representation; derivation paths.

# The foundational question

What would it mean to make ordinal arithmetic the underlying foundation of a Tarski-definable arithmetic? The phrase needs a language and a domain of definability. In this paper it means that the truth and satisfaction relations for an arithmetic object language are definable in a specified richer framework, with explicit ordinal bounds on the languages to which each truth predicate applies. It does not mean decidability of arithmetic or an unrestricted truth predicate definable inside its own language.

Here "ordinal-first" refers to the arithmetic domain and the ordering of semantic dependencies. The ambient metalanguage is the set theory specified below; the paper does not assert definability of arithmetic truth in the ordinal-arithmetic structure alone.

We use *Ordinatics* as the name of the overall framework. The motivating notes distinguish a layer of ordinary ordinal operations, an intended extension admitting reciprocals and fractional powers, and a further complex-valued extension \[17\]. We retain these as distinct layers within Ordinatics. They also distinguish derivation-path identity, written $=$ in those notes, from outcome congruence $\equiv$ and continuation similarity $\sim$. This separation suggests that an expression should retain more information than its numerical image. We preserve that design question while making the mathematical interpretation explicit.

Three roles of ordinals must be distinguished. First, finite ordinals carry ordinary arithmetic. Second, transfinite ordinals organize the dependencies of semantic definitions. Third, ordinal expressions can motivate algebraic expressions that admit division. These roles can coexist in a typed framework, but their operations need not agree. An ordinal rank is not automatically a field value, and a field value is not a truth predicate.

The established background is the definition of truth through satisfaction and the restriction on truth definitions for semantically closed languages \[1\]. Typed and ordinal-indexed truth hierarchies are also established constructions \[2\]. Feferman's work studies transfinite progressions of axiomatic theories \[5\], and a modern proof and complexity analysis makes the associated arithmetic completeness theorem explicit \[6\]. Iterated Tarskian truth, induction, and reflection have been connected directly in proof-theoretic analyses \[3\], \[4\]. Recursive and cyclic representations of proofs with global correctness conditions form another developed literature \[10\], \[11\]. Recent Reflective Grounded Arithmetic gives machine-checked same-language proof machinery and internal truth under paracomplete grounded semantics \[8\], \[9\]. Our construction below begins as a classical semantic hierarchy, not an identification with any of those systems. No priority claim is made for ordinal-indexed truth hierarchies, completeness of reflection progressions, recursive proof graphs, internal proof checking, polynomial fields, or localization. The project-specific open target is a sound bridge from the native path-retaining record calculus to a named reflection progression covering standard classical arithmetic truth. Establishing its novelty requires comparison with these adjacent systems as well as completion of the bridge.

#### Ambient assumptions.

We work in ordinary classical mathematics formalizable in Zermelo--Fraenkel set theory with the Axiom of Choice, abbreviated ZFC. Its operational role is to supply sets, finite syntax, and transfinite recursion, not a numerical unit. All quantities below are mathematical objects with no physical dimension. The use of this metatheory is explicit: the paper does not derive its set existence assumptions from the source notes' $\square$ ground-and-term-former. A faithful internal derivation in that system remains a separate research obligation.

# Ordinal arithmetic without a change of operations

Let $\omega$ be the least infinite ordinal. Write $+_o$ and $\cdot_o$ for ordinary ordinal addition and multiplication, defined recursively in the right argument. In particular, $$\begin{align*}
\alpha+_o0&=\alpha,&\alpha+_o(\beta+1)&=(\alpha+_o\beta)+1,\\
\alpha\cdot_o0&=0,&\alpha\cdot_o(\beta+1)&=(\alpha\cdot_o\beta)+_o\alpha.
\end{align*}$$ At a nonzero limit, take the supremum of the earlier values. This is the standard ordinal recursion construction \[12\]. It gives $$1+_o\omega=\omega,\qquad \omega+_o1>\omega,
\qquad 2\cdot_o\omega=\omega,\qquad \omega\cdot_o2=\omega+_o\omega.$$ Thus even the expression "twice an ordinal" needs an operand order.

#### Proposition 2.1 (Absorption obstructs a unital additive field interpretation).

Suppose a domain contains $1,\omega$ and $1+_o\omega=\omega$. There is no map $f$ into the additive group of a nontrivial field such that $f(1)=1$ and $f(\alpha+_o\beta)=f(\alpha)+f(\beta)$ on these inputs.

#### Proof.

The absorption equation would imply $1+f(\omega)=f(\omega)$. Cancellation gives $1=0$, contradicting nontriviality.

This obstruction does not depend on injectivity or on the field being Archimedean. Passing to an ordered field with infinite elements does not repair it. One may introduce new field operations on representations of ordinals, but that is a change of operations and must be marked as such.

For a concrete set-sized ordinal domain, fix $$\theta=\omega^\omega,\qquad \mathcal O=\{\alpha:\alpha<\theta\},
\qquad \mathcal A=(\mathcal O,0,1,\omega,<,+_o,\cdot_o).$$ Every element has a unique finite ordinal polynomial representation $$\alpha=\omega^k a_k+_o\cdots+_o\omega a_1+_o a_0,
\quad a_j\in\mathbb N,$$ where coefficients multiply on the right and the leading coefficient is nonzero unless $\alpha=0$. Finite addition and multiplication of these ordinals remain below $\theta$: the highest exponent of a sum is at most the maximum of the input exponents, and that of a nonzero product is at most their sum. This representation is the restricted Cantor normal form. It gives computable finite codes and a computable comparison relation for the ranks used below. The bound is a convenient concrete choice, not a proposed ultimate ordinal of the theory.

#### Proposition 2.2 (Arithmetic as a definable finite-ordinal part).

In $\mathcal A$, the formula $x<\omega$ defines a domain whose induced $0,1,+_o,\cdot_o$ structure is the standard arithmetic structure $(\mathbb N,0,1,+,\cdot)$.

#### Proof.

The ordinals below $\omega$ are exactly the finite ordinals. The displayed recursions restrict to the usual addition and multiplication recursions on them. Relativize every arithmetic quantifier to $x<\omega$. Induction on terms and formulas shows that this translation preserves satisfaction.

Consequently an ordinal foundation retains arithmetic's capacity to encode syntax. Replacing natural-number notation with ordinal notation does not by itself remove diagonalization. The proposition establishes a definable arithmetic domain; it does not establish a definable truth predicate in $\mathcal A$.

# A bounded value layer for Ordinatics

The source wrap anchor $W(\omega)=-1/2$ is useful as a proposed numerical evaluation. To interpret it coherently, introduce an indeterminate $X$ distinct from the ordinal $\omega$. Let $$K=\mathbb Q(X),\qquad c=-\tfrac12,
\qquad S=\{q\in\mathbb Q[X]:q(c)\ne0\},\qquad R=S^{-1}\mathbb Q[X].$$ Here $K$ is the field of rational functions. The ring $R$ consists of rational functions admitting a representation with denominator nonzero at $c$; this is the standard localization construction \[14\]. Define $$W:R\longrightarrow\mathbb Q,\qquad W(p/q)=p(c)/q(c).$$ We call $K$ a *bounded value model of Ordinatics*: it realizes division in a value layer motivated by ordinal forms. It is not asserted to be the full Subreal type of the notes, an algebraically closed field, or a model of every $\square$ axiom.

#### Theorem 3.1 (Scope of wrap specialization).

The map $W$ is a well-defined surjective unital ring homomorphism on $R$. Its kernel is $(X-c)R$. It cannot extend to a unital field homomorphism $K\to\mathbb Q$. An element $r\in R$ is a unit of $R$ (has a multiplicative inverse in $R$) if and only if $W(r)\ne0$.

#### Proof.

If $p/q=p'/q'$ then $pq'=p'q$; evaluating at $c$ and dividing by the nonzero denominators proves well-definedness. Evaluation respects sums and products and fixes rational constants, which also proves surjectivity. A polynomial vanishes at $c$ exactly when it is divisible by $X-c$, giving the kernel assertion. In $K$, the nonzero element $X-c$ has an inverse. An extension would send $(X-c)(X-c)^{-1}=1$ to $0\cdot W((X-c)^{-1})=1$, a contradiction. Finally, if $r=p/q$ and $W(r)\ne0$, then $p(c)\ne0$ and $q/p\in R$. Conversely, an inverse in $R$ would give $W(r)W(r^{-1})=1$.

This construction recovers $W(X^n)=(-1/2)^n$ for every integer $n$, including $W(X^{-1})=-2$. It also exposes a necessary limitation: $2X+1$ is a nonzero field element with wrap value zero, so its inverse has no wrap value under this specialization. Undefined evaluation is distinct from zero evaluation.

There is a faithful *representation map* $$j:\mathcal O\longrightarrow\mathbb N[X]\subset K,\qquad
j(\omega^k a_k+_o\cdots+_o a_0)=a_kX^k+\cdots+a_0.$$ It is a bijection onto polynomials with nonnegative integer coefficients, by uniqueness of the normal form. Pulling polynomial addition and multiplication back along $j$ gives commutative operations $\oplus,\otimes$ on $\mathcal O$. By construction, $$j(\alpha\oplus\beta)=j(\alpha)+j(\beta),\qquad
j(\alpha\otimes\beta)=j(\alpha)j(\beta).$$ They agree with ordinary arithmetic on finite ordinals, but $1\oplus\omega=\omega+_o1$ whereas $1+_o\omega=\omega$. These are the natural ordinal operations on this restricted domain; their distinction from ordinary ordinal operations is essential. The field is generated by $j(\mathcal O)$ over $\mathbb Q$, but $j$ is not an embedding for $+_o,\cdot_o$.

## Fractional powers and branch data

If fractional monomials are added, choose a coherent branch explicitly. For instance, with $\ell=-\log 2+i\pi$, the map $$\chi:(\mathbb Q,+)\longrightarrow(\mathbb C\setminus\{0\},\cdot),
\qquad \chi(r)=\exp(r\ell)$$ satisfies $\chi(r+s)=\chi(r)\chi(s)$ and $\chi(1)=c$. However, $\chi(1/3)=2^{-1/3}e^{i\pi/3}$ is not the real cube root $-2^{-1/3}$. Choosing a real cube root at $1/3$ and the principal value $2^{-1/6}e^{i\pi/6}$ at $1/6$ violates $\chi(1/3)=\chi(1/6)^2$. A mixed root convention is therefore not a single multiplicative character. Also, a collection of nonzero monomial values is not itself a field: it does not contain zero, let alone automatically supply all sums.

For complex $z$, the same expression $\Phi(z)=\exp(\ell z)$ is surjective onto $\mathbb C\setminus\{0\}$, but $$\Phi(z)=\Phi(z')\quad\Longleftrightarrow\quad
z-z'\in\frac{2\pi i}{\ell}\mathbb Z.$$ This follows from the kernel of the complex exponential. Thus $\Phi$ induces a bijection from the quotient by that lattice onto $\mathbb C\setminus\{0\}$. Restricting its domain to the half-open strip $-\pi<\operatorname{Im}(\ell z)\le\pi$ also gives a set bijection onto $\mathbb C\setminus\{0\}$, but its inverse is discontinuous across the negative real axis. An analytic logarithm branch instead uses a slit codomain, for example $\mathbb C\setminus(-\infty,0]$ \[15\]. A numerical image generally does not identify its source expression. Neither the real-root convention nor complex injectivity is needed for the truth construction below.

# Expressions, outcomes, and information loss

Let $\mathcal E$ be finite typed expression trees. Ordinal constructors use $+_o,\cdot_o$; field constructors use $+_K,\cdot_K$ and inversion of nonzero field values; $j$ is an explicit conversion on normalized ordinal values. An expression has its syntax tree, its typed denotation, and, where applicable, its wrap evaluation. These are different data.

The source relations motivate the following limited correspondence. Literal tree identity models one precise notion of path identity. Equal typed denotations model outcome congruence. Equal wrap values give a still coarser comparison on the wrap domain. This is a proposed mathematical interpretation, not a proof that these relations equal the source's full $=,\equiv,\sim$ filtration. In particular, continuation similarity has not been supplied with a transition system here. Nonempty overlap of continuation sets need not be transitive, so quotienting by it would require an additional argument.

Two short examples show why the distinctions matter. The ordinal expression trees for $1+_o\omega$ and $\omega$ differ but have the same ordinal value. In contrast, the ordinals $\omega\cdot_o2+_o1$ and $0$ differ, while $$W(j(\omega\cdot_o2+_o1))=W(2X+1)=0=W(j(0)).$$ Neither syntactic identity nor ordinal identity can be reconstructed from this wrap value.

#### Lemma 4.1 (Ranks cannot be recovered from a collapsed evaluation).

If a map $e$ identifies two ranks $a<b$, there is no irreflexive relation $\prec$ on its image satisfying $e(a)\prec e(b)$ whenever $a<b$.

#### Proof.

For the identified pair the required relation would read $e(a)\prec e(a)$, violating irreflexivity.

The operational consequence is specific: a wrap value alone cannot serve as a truth-level identifier if distinct comparable levels share it. Keep the original rank and the expression record alongside the value.

Regularized sums require a similar precaution. The ordinary ordinal sums $1+_o1+_o\cdots$ and $1+_o2+_o3+_o\cdots$ both have supremum $\omega$, since their finite partial sums are unbounded finite ordinals. Any assignments of different regularized values therefore act on tagged summation expressions or additional analytic data, not solely on their resulting ordinal. This paper does not assume a summation regularization or derive a negative finite value for an ordinary divergent sum.

# An ordinal-indexed language of arithmetic truth

Let $L_0=\{0,1,+,\cdot,<\}$ be the first-order language of arithmetic, with equality. Fix an injective effective coding into $\mathbb N$ of finite terms and formulas, including canonical finite-tuple codes for ordinal polynomial indices below $\theta$. Choose the coding so that parsing, numeral formation, and capture-avoiding substitution are computable, as with the usual coding of finite strings over an effectively indexed vocabulary. The symbol $T_\beta$ is a unary predicate for each $\beta<\theta$. For $\alpha\le\theta$, put $$L_\alpha=L_0\cup\{T_\beta:\beta<\alpha\}.$$ The predicate $T_\alpha$ will express truth for *sentences of $L_\alpha$*; it first occurs in $L_{\alpha+1}$ when that language is within the chosen range. At $\theta$ we construct the truth set externally without adding its symbol to $L_\theta$.

#### Effective syntax, not effective truth.

Ordinal polynomial codes can be checked and compared by finite algorithms. For each fixed $\alpha<\theta$, membership of a predicate index in $L_\alpha$ is decidable; at $\theta$, all valid indices are allowed. Coding, substitution, and the formation of numerals can consequently be carried out arithmetically. This does not supply an algorithm for the truth sets. Computable level names and computable semantic contents are different assertions.

Write $\operatorname{Sent}(L_\alpha)$ for codes of closed $L_\alpha$ formulas. At each stage the underlying arithmetic domain is the finite-ordinal domain $\mathbb N$. Truth predicates act on numbers that code sentences, not on ordinal values returned by $W$.

#### Definition 5.1 (Staged structures and truth sets).

For $\alpha\le\theta$, define recursively $$\begin{align}
M_\alpha&=(\mathbb N,0,1,+,\cdot,<,(\mathsf{Tr}_\beta)_{\beta<\alpha}),\label{eq:structure}\\
\mathsf{Tr}_\alpha&=\{n\in\operatorname{Sent}(L_\alpha):M_\alpha\models\varphi_n\},\label{eq:truth}
\end{align}$$ where $\varphi_n$ is the sentence coded by $n$. Numbers that do not code such a sentence are not in $\mathsf{Tr}_\alpha$.

This definition has two recursions. The outer recursion is on $\alpha$. The inner satisfaction recursion is on formula construction with the interpretations of earlier predicates already fixed. Explicitly, for an assignment $s$ of natural numbers to variables, $$\begin{align*}
\operatorname{Sat}_\alpha(t=u,s)&\ \Longleftrightarrow\ t^{M_\alpha}[s]=u^{M_\alpha}[s],\\
\operatorname{Sat}_\alpha(t<u,s)&\ \Longleftrightarrow\ t^{M_\alpha}[s]<u^{M_\alpha}[s],\\
\operatorname{Sat}_\alpha(T_\beta(t),s)&\ \Longleftrightarrow\ t^{M_\alpha}[s]\in\mathsf{Tr}_\beta\quad(\beta<\alpha),\\
\operatorname{Sat}_\alpha(\neg\psi,s)&\ \Longleftrightarrow\ \neg\operatorname{Sat}_\alpha(\psi,s),\\
\operatorname{Sat}_\alpha(\psi\land\eta,s)&\ \Longleftrightarrow\ \operatorname{Sat}_\alpha(\psi,s)\land\operatorname{Sat}_\alpha(\eta,s),\\
\operatorname{Sat}_\alpha(\exists x\,\psi,s)&\ \Longleftrightarrow\ \exists n\in\mathbb N\ \operatorname{Sat}_\alpha(\psi,s[x\mapsto n]).
\end{align*}$$ Other connectives and the universal quantifier are defined from these. Satisfaction for open formulas is therefore included; the truth sets are their closed-sentence restriction.

#### Theorem 5.2 (Existence, uniqueness, and external definability).

In the stated metatheory, there is a unique hierarchy $(\mathsf{Tr}_\alpha)_{\alpha\le\theta}$ satisfying (1)--(2). Membership in this hierarchy and the associated satisfaction relations are definable in that metatheory from the fixed coding and ordinal bound.

#### Proof.

Given the sequence of truth sets below $\alpha$, equation (1) specifies a set-sized structure in a set-sized language. The displayed formula recursion constructs its satisfaction relation: atomic clauses are fixed, and each composite clause uses only proper subformulas. Assignments may be taken to be finite sequences long enough for the formula's variables. The relevant formulas and assignments form a set, so this recursion defines a set relation. Separation then yields (2). This rule is a definable function of the earlier sequence. Transfinite recursion up to $\theta+1$ gives existence. For uniqueness, a least stage of disagreement would have identical earlier predicates; formula induction gives identical satisfaction at that stage and hence identical truth sets, a contradiction. The recursive characterization is a set-theoretic definition of the sequence and its membership relation.

This establishes truth *in* the metatheory, not an algorithm deciding it and not truth *of* that metatheory. In a nonstandard model of the metatheory, the internal natural numbers and internal satisfaction construction must be distinguished from the intended external standard objects. No absoluteness across arbitrary models is claimed.

#### Theorem 5.3 (Stage compatibility and typed disquotation).

If $\alpha\le\gamma\le\theta$, the reduct of $M_\gamma$ to $L_\alpha$ is $M_\alpha$. Consequently $L_\alpha$ formulas have the same satisfaction value at these stages. If $\alpha<\gamma$, then for every $L_\alpha$ sentence $\varphi$, $$M_\gamma\models T_\alpha(\ulcorner \varphi\urcorner)\leftrightarrow\varphi.$$ Here a code inside a formula denotes its standard numeral.

#### Proof.

All structures have the same arithmetic part, and every earlier predicate keeps the set assigned at its defining stage. Term and formula induction proves the reduct assertion. The truth definition then gives the displayed equivalence.

Stage compatibility concerns the intended models. It is not a conservativity theorem for recursively axiomatized proof systems, because none has been specified.

## Ranks and limit stages

Define the static language rank of an arithmetic atom to be $0$, that of $T_\beta(t)$ to be $\beta+1$, that of a negation or quantification to be the subformula rank, and that of a conjunction to be the maximum of its two ranks. For a well-formed formula $\varphi$ over $L_\theta$, $\varphi$ is an $L_\alpha$ formula exactly when $\operatorname{rk}(\varphi)\le\alpha$. This rank measures which predicate symbols occur; it need not measure the depth of truth references hidden in a numeral supplied to a predicate.

At a nonzero limit $\lambda\le\theta$, every $L_\lambda$ formula uses finitely many earlier predicate symbols, so it already belongs to some $L_\alpha$ with $\alpha<\lambda$. Stage compatibility therefore yields $$\mathsf{Tr}_\lambda=\bigcup_{\alpha<\lambda}\mathsf{Tr}_\alpha.$$ No infinitary conjunction has been silently added. Successor stages add a new truth predicate to the language; limit stages collect all earlier finite sentences and their stable interpretations.

For example, let $\varphi$ be $1+1=1+1$. It is true in $M_0$, and $T_0(\ulcorner \varphi\urcorner)$ is true in $M_1$. The sentence $T_1(\ulcorner T_0(\ulcorner \varphi\urcorner)\urcorner)$ is true in $M_2$. At level $\omega+1$, $T_\omega$ can refer to any sentence involving finitely many finite-level predicates. These are semantic examples, not computed decisions of arbitrary arithmetic sentences.

# Fractal meta-representation: the completeness target

The adjective *fractal* is used here in a syntactic, not geometric, sense. The repeated pattern is that a closed derivation becomes a typed record in the same grammar, its acceptance is again represented by a closed derivation, and that derivation may itself be reified at a later rank. The phrase carries no physical dimension and asserts no fractal dimension. A finite cyclic record may denote an infinite unfolding only after a global validity condition has been specified. Existing cyclic proof systems demonstrate that finite recursive proof graphs and global trace conditions are mathematically workable, while also showing that the trace condition and its soundness proof are substantive parts of the calculus \[10\], \[11\].

#### Definition 6.1 (Ranked self-closing meta-surface).

Let $\Lambda$ be a nonzero limit ordinal. For each $\alpha<\Lambda$, let $S_\alpha$ be a set of well-typed native expressions, let $D_\alpha$ be a set of closed native derivations, and let $c_\alpha:D_\alpha\to S_\alpha$ give their conclusions. Require cumulative inclusions for earlier ranks, with the conclusion maps preserved, and require $$S_\lambda=\bigcup_{\alpha<\lambda}S_\alpha,
\qquad
D_\lambda=\bigcup_{\alpha<\lambda}D_\alpha$$ at each nonzero limit $\lambda<\Lambda$. For every $\alpha$ with $\alpha+1<\Lambda$, supply a reification map $e_\alpha:D_\alpha\to S_{\alpha+1}$, an acceptance-forming constructor $$\mathsf{Acc}_{\alpha+1}:S_{\alpha+1}\times S_\alpha\to S_{\alpha+1},$$ and an acceptance-derivation map $v_\alpha:D_\alpha\to D_{\alpha+1}$ satisfying $$c_{\alpha+1}(v_\alpha(d))
=\mathsf{Acc}_{\alpha+1}(e_\alpha(d),c_\alpha(d)).$$ Such a family is a *ranked self-closing meta-surface*. It is self-closing because each acceptance derivation $v_\alpha(d)$ is eligible for reification at the next rank. Call it *internally self-derivable* relative to native rule systems $(\mathcal R_\alpha)_{\alpha<\Lambda}$ when each $D_\alpha$ consists of the closed derivations generated by $\mathcal R_\alpha$ and $v_\alpha$ is a rule-defined constructor whose output is checkable as an $\mathcal R_{\alpha+1}$ derivation. This is a syntactic condition. Calling its accepted conclusions semantically valid additionally requires a soundness theorem. The successor shift is part of the typing discipline; the definition supplies no same-rank predicate for the full truth of $S_\alpha$.

An Ordinatics instance must place the translated rank-$\alpha$ arithmetic expressions and claims in $S_\alpha$. It is Hypermath-derived only when the sets, derivations, reification maps, acceptance constructor, acceptance-derivation maps, and any claimed native rule checkers are constructed from a specified Hypermath grammar and its inference rules. The displayed definition is an abstract interface. The current Hypermath source does not yet supply this complete instance, its arithmetic interpretation, or the soundness theorem for $\mathsf{Acc}$.

#### Definition 6.2 (Observation-exact reification).

Let $\mathcal D$ be a set of derivations, $\mathcal R$ a set of records, $\mathcal Q$ a set of admissible observations, and $B$ a set of outcomes. For an encoding $e:\mathcal D\to\mathcal R$ and an observation semantics $b:\mathcal D\times\mathcal Q\to B$, say that $e$ is observation-exact for $\mathcal Q$ if there is a decoder $\bar b:e[\mathcal D]\times\mathcal Q\to B$ such that $$\bar b(e(d),q)=b(d,q)
\qquad(d\in\mathcal D,\ q\in\mathcal Q).$$

#### Theorem 6.3 (Reification factorization criterion).

An observation-exact decoder exists if and only if, for all $d,d'\in\mathcal D$ and $q\in\mathcal Q$, $$e(d)=e(d')\quad\Longrightarrow\quad
b(d,q)=b(d',q).$$ When it exists, the decoder is unique on $e[\mathcal D]\times\mathcal Q$.

#### Proof.

If a decoder exists, equal records receive equal decoded outcomes, which gives the displayed implication. Conversely, for $r\in e[\mathcal D]$ choose any $d$ with $e(d)=r$ and put $\bar b(r,q)=b(d,q)$. The implication makes this value independent of the chosen preimage, and it also gives uniqueness.

Literal recovery of an entire derivation is sufficient for this criterion, but is not necessary. A pointer to a retained derivation preserves its information only because the pointed-to store remains part of the representation. If an encoding collapses records that differ on stage, formula, dependency, branch, or global-trace evidence, then those features cannot be recovered by a decoder. In particular, the value $W(j(\alpha))$ cannot replace the ordinal rank and derivation record; Lemma 4.1 already shows the obstruction when comparable ranks collapse.

#### Proposition 6.4 (Preservation under finite reuse).

Fix an observation-exact encoding $e:\mathcal D\to\mathcal R$ for $b$. Let $(c_i:\mathcal D\to\mathcal D)_{i\in I}$ be permitted reuse operations such that $$e(d)=e(d')\quad\Longrightarrow\quad e(c_i(d))=e(c_i(d'))
\qquad(i\in I).$$ For every finite composite $c=c_{i_n}\circ\cdots\circ c_{i_1}$, including the identity, the observations $(d,q)\mapsto b(c(d),q)$ factor through $e$.

#### Proof.

Induction on the number of operations shows that $e(d)=e(d')$ implies $e(c(d))=e(c(d'))$. Observation-exactness then gives $b(c(d),q)=b(c(d'),q)$ for every $q$. Apply the factorization criterion.

The premise about each operation is essential to this sufficient condition. For example, projecting a pair of bits onto its first bit preserves first-bit queries and remains adequate under arbitrary first-bit flips. Swapping the bits exposes the discarded second bit: $(0,0)$ and $(0,1)$ have the same encoded record but yield different observations after the swap. A correct base decoder alone therefore does not certify reuse. This proposition concerns finite contexts for a fixed encoding. Applying it to ranked self-closing surfaces still requires suitable typed representations and operation laws; it supplies no limit-stage rule or native acceptance constructor.

#### Proposition 6.5 (Native numeral equality requires separation).

For an encoding $E:\mathbb N\to\mathcal F$, put $b(n,k)=1$ when $n=k$ and $b(n,k)=0$ otherwise. These equality queries have an exact decoder on $E[\mathbb N]$ if and only if $E$ is injective.

#### Proof.

If $E(n)=E(m)$, the factorization criterion gives $b(n,n)=b(m,n)$. The left side is $1$, so $m=n$. Conversely, injectivity makes every fiber contain exactly one input, and hence the criterion holds for these queries.

These results have checked Lean counterparts in the reviewed Hypermath source \[16\]. Decoder existence uses classical choice, including when factorization is applied after reuse. The generic lemmas for finite-reuse preservation of equal observations and equivalence of injectivity with the equality-query factorization premise have no axiom dependencies. Specializing $E(n)=\mathrm{f2f}^{n}(\mathrm{ground})$ uses the existing native parameters without adding a logical clause. In the six-Form model of all 38 declared logical clauses, $E(1)=E(3)$, so no such equality-query decoder exists, although addition and multiplication respect equality of represented values. The model refutes this encoding's adequacy for the original natural-number equality observations. It does not exclude every alternative native encoding. Injectivity, when available, would still leave the native checker, arithmetic operations, quantifiers, and soundness to be connected.

The semantic hierarchy of Section 5 contains no proof predicate or recursively axiomatized progression. The nearest established proof-theoretic comparison starts with Peano arithmetic, abbreviated $\mathsf{PA}$, and iterates full uniform reflection. Schematically, if $U$ is a recursively presented arithmetic theory, its full uniform reflection scheme contains $$\forall \vec x\bigl(\operatorname{Pr}_{U}(\ulcorner
\varphi(\dot{\vec x})\urcorner)\to\varphi(\vec x)\bigr)$$ for each arithmetic formula $\varphi$, where $\operatorname{Pr}_{U}$ is the arithmetized proof predicate and the dots denote numeral substitution. A notation-indexed progression has $U_0=\mathsf{PA}$, adds this scheme at successor notations, and takes the indicated union at limit notations. This description is schematic until the ordinal-notation system, predecessor relation, limit presentation, proof coding, and accepted well-foundedness evidence are fixed.

Feferman's completeness theorem and its modern sharp bound give the external coverage statement $$\mathbb N\models\varphi
\quad\Longrightarrow\quad
\exists a\in\mathcal O_{\mathrm K}\,
\bigl(|a|<\omega^\omega\ \land\ U_a\vdash\varphi\bigr)$$ for every arithmetic sentence $\varphi$, where $|a|$ is the ordinal denoted by the Kleene notation $a$ \[5\], \[6\]. More precisely, a true $\Pi_{2n+1}$ sentence can be reached at a notation of order type $\omega^{n+1}+1$ \[6\]. This external coverage across a family must be distinguished from stagewise completeness: no fixed sound recursively enumerable stage is thereby claimed to decide all arithmetic truth. It also supplies neither effective decidability nor an effective procedure that selects a valid notation from $\varphi$. Membership in $\mathcal O_{\mathrm K}$ is itself not an arithmetical decision problem. Moreover, the theory reached can depend on the notation and path, not only on the denoted ordinal; Feferman records both the completeness of suitable full-uniform-reflection paths and the failure of invariance across arbitrary paths \[7\]. The bound explains the use of $\omega^\omega$ here, but a canonical polynomial code for an ordinal below that bound is not thereby a Kleene notation or a well-foundedness certificate.

The connection between iterated Tarskian truth and reflection is itself established: Beklemishev and Pakhomov analyze transfinitely iterated truth definitions with reflection and canonical ordinal notations, while Leigh characterizes iterated reflection over typed and disquotational truth theories \[3\], \[4\]. Reflective Grounded Arithmetic, abbreviated RGA, is still closer to the same-language machinery: recent machine-checked developments internalize proof checking and truth in a paracomplete arithmetic \[8\], \[9\]. Its open completeness concerns grounded truth and coexists with $\omega$-incompleteness; it does not claim classical coverage of all standard arithmetic truth. The target here instead retains classical semantics and asks for a path-retaining native realization of the external reflection coverage above.

This comparison gives a precise reading of the project's phrase *Gödelian complete ordinal arithmetic*: sound external coverage of standard arithmetic truth by a transfinite family of stages, with notation and derivation evidence retained. It does not mean decidability, truth definable in its own object language, or a recursively enumerable theory that proves every arithmetic truth.

#### Theorem 6.6 (Conditional record coverage).

Let $\mathcal O$ be an accepted notation class and $(U_a)_{a\in\mathcal O}$ have the external coverage property above. Let $\mathcal A$ be the set of arithmetic sentences and let $$\mathcal D=\{(a,p):a\in\mathcal O,\ p\in\mathbb N\}$$ be the set of notation and candidate-proof-code pairs. Define the proof observation $b:\mathcal D\times\mathcal A\to\{0,1\}$ by $$b((a,p),\varphi)=1
\quad\Longleftrightarrow\quad
\operatorname{Proof}_{U_a}(p,\varphi).$$ Let $e:\mathcal D\to\mathcal R$ be observation-exact for these sentence queries, with decoder $\bar b:e[\mathcal D]\times\mathcal A\to\{0,1\}$. Suppose a native calculus $H$ supplies a translation $\iota$ and a record-only checker $\mathsf{Check}_H$ such that $$\mathsf{Check}_H(r,\iota(\varphi))=\bar b(r,\varphi)
\qquad(r\in e[\mathcal D],\ \varphi\in\mathcal A),$$ and suppose the checker is arithmetically sound: $$\mathsf{Check}_H(r,\iota(\varphi))=1
\quad\Longrightarrow\quad
\mathbb N\models\varphi
\qquad(r\in e[\mathcal D],\ \varphi\in\mathcal A).$$ Then, for every arithmetic sentence $\varphi$, $$\mathbb N\models\varphi
\quad\Longleftrightarrow\quad
\exists r\in e[\mathcal D]\;
\mathsf{Check}_H(r,\iota(\varphi))=1.$$

#### Proof.

For the forward direction, external coverage supplies a notation $a$ and a code $p$ that proves $\varphi$. The proof observation therefore equals one. Observation-exactness and checker agreement show that the reified record is accepted for $\iota(\varphi)$. The reverse direction is the checker-soundness assumption.

The conclusion refers to the native record alone; the external proof code appears only in the construction of that record. Observation-exactness prevents an encoding from merging proof packages that the checker must distinguish. The checker-agreement equation is still a substantive realization obligation, and soundness must be proved independently of the truth it is intended to establish. For $\iota$ to be a structure-preserving arithmetic interpretation, it must preserve arithmetic operations, negation, and quantification. A realization as a ranked self-closing meta-surface must additionally place each record and its acceptance derivation at the specified successor ranks. Accepted notation evidence and any cyclic global condition must be checked by stated rules.

If $\iota$ is computable, $e[\mathcal D]$ is effectively enumerable, and $\mathsf{Check}_H$ is uniformly decidable, total sound coverage would decide arithmetic truth by parallel searches for records checking a sentence and its negation. At least one of those effectiveness properties must therefore fail for full classical coverage.

The current Hypermath development supplies finite traces, a proposed self-derivation target, and explicit audit surfaces, but its checked countermodels separate that target from the required arithmetic action and interpretation bridges \[16\]. Neither that development nor the Python companion below currently supplies the ranked surface, checker agreement, arithmetic interpretation, or soundness hypothesis of the record-coverage theorem. Their recursively grounded arithmetic completeness status is therefore unresolved, rather than established by the conditional result.

#### A finite source-syntax realization.

The reviewed Hypermath development now constructs a bounded instance of record representation \[16\]. Let $T$ be the free finite term grammar $t::=\square\mid\operatorname{apply}(t)$, taken from the formation syntax of the source's ground layer. Let $D_0$ contain the ground-self rule and the three parameterized rule schemata $\operatorname{diff}(t)$, $\operatorname{sim}(t)$, and $\operatorname{box}(t)$. Their conclusions are, respectively, that ground continues from itself, that $\operatorname{apply}(t)$ is structurally distinct from ground, that it continues from ground, and that $\operatorname{apply}^2(t)$ structurally orbits $t$. These are three separate binary predicates; no identification with equality is made.

Encode a ground-self instance as the depth-zero term. For an argument of depth $d$, encode the other three tags at term depths $4d+1$, $4d+2$, and $4d+3$. The decoder $\delta:T\to D_0\cup\{\bot\}$ reverses this assignment and rejects positive multiples of four. Here $\bot$ denotes decoding failure, not a false arithmetic sentence. Define $\operatorname{check}(r,s)=1$ exactly when $r$ decodes and its decoded instance has syntactic conclusion $s$. The decoder takes the record alone; the checker additionally takes the claimed statement. This unary code makes no compression claim.

#### Proposition 6.7 (Primitive records and finite rule reuse).

For this encoding $e:D_0\to T$, $\delta(e(p))=p$ for every $p\in D_0$. Consequently $e$ is injective and every observation of $p$ can be recovered from $e(p)$. In every interpretation satisfying the four primitive source-rule schemata, $\operatorname{check}(r,s)=1$ implies that $s$ holds. Let $u$ replace each parameterized rule's argument $t$ by $\operatorname{apply}(t)$ and leave the ground-self instance unchanged. Define $R$ on decodable records by $R(e(p))=e(u(p))$. Then for every finite $n$ and $p\in D_0$, $R^n(e(p))=e(u^n(p))$, and the result checks against the conclusion of $u^n(p)$.

#### Proof.

Depth zero identifies the ground-self rule. Otherwise the depth modulo four identifies the rule tag, and removing that tag and dividing the remaining depth by four recovers the argument's depth, hence its unique free term. This proves the round trip and injectivity; composing the decoder with any observation proves observation recovery. An accepted statement is exactly a decoded rule instance's conclusion, so its validity follows from the corresponding rule premise in the interpretation. Induction on $n$ proves the reuse equation, and the round trip gives acceptance of its resulting record.

The Lean counterparts include `decode_encode`, `check_sound`, and `reuse_many_encode`. The native soundness specialization uses the existing source parameters and four primitive clauses, with no new native axiom, admission, or classical-choice dependency. Lean's inductive types, recursion, propositional extensionality, and quotient equality principle remain explicit host infrastructure. This construction represents primitive instances. The extension below encodes composed derivations; neither construction internalizes the checker or derives its own acceptance statements at a new rank.

Free terms must also be distinguished from their semantic interpretation as `Form` values. In the six-Form model of all 38 source clauses, the depth-one and depth-three records for $\operatorname{diff}(\square)$ and $\operatorname{box}(\square)$ have the same interpretation but different syntactic conclusions. Therefore no decoder of that semantic value alone recovers every original instance under this encoding. Both conclusions can hold in the model; the obstruction concerns record recovery, not consistency of the primitive rules. A native reification theorem must preserve the observations required after interpretation. The finite construction does not discharge that obligation or the hypotheses of the conditional coverage theorem.

#### Composed records and retained formation trees.

Extend the finite formula grammar with similarity, negated simulation, and conjunction. A typed derivation is generated by the four primitive schemata, the forward directions of the three source predicate closes, conjunction introduction, and the two projections. The closes infer similarity to ground from continuation to ground, negated simulation from structural distinctness, and similarity of $\operatorname{apply}^2(t)$ to $t$ from its structural orbit. Conjunction has the host logical interpretation already used by the source; adequacy for its native proposition type remains an obligation.

A raw record retains every rule name, term argument, premise record, and projection annotation. Let $K(r,s)$ first check every premise and required annotation, then compare the computed conclusion with $s$. Let $q(d)$ quote a typed derivation as a raw record, and let $\rho(r)$ reconstruct the typed derivation after successful checking. Reconstruction takes the record alone; its Boolean check supplies the evidence needed by the typed constructor.

#### Proposition 6.8 (Composed checking and exact record reconstruction).

Every typed derivation $d$ with conclusion $c(d)$ satisfies $K(q(d),c(d))=1$. Every accepted record satisfies $q(\rho(r))=r$. Consequently all observations of its formation tree survive reconstruction. A formula has an accepted record exactly when it is derivable in this finite calculus. Every accepted conclusion holds in each interpretation satisfying the four primitive and three predicate-close premises.

#### Proof.

Induct on the typed derivation for acceptance and soundness. Primitive cases use their corresponding source clauses, closes use the stated forward implications, and conjunction rules use introduction or elimination. For reconstruction, induct on the raw record. Its acceptance check gives accepted premises with the required conclusions; reconstruct them inductively and apply the indicated typed rule. Quoting that result returns the same rule, arguments, annotations, and premise records. The two constructions give the representability equivalence. Composing the exact round trip with any function of a record proves observation preservation.

The equivalence is checker coverage of the specified calculus, not semantic completeness for its models or arithmetic truth. Checking a projection includes its entire conjunction premise; a valid selected branch cannot hide a failed unselected branch.

#### Single-term codes and their cost.

Represent each constructor and its arguments by a tagged finite binary tree. Encode a leaf by bit $0$, and a fork by bit $1$ followed by its two child codes. The parser must consume the complete input. Pack a bit list into a natural number by $P([])=0$, $P(0::b)=2P(b)+1$, and $P(1::b)=2P(b)+2$. Tag the outer record and formula trees differently. Write $E(r)$ and $F(s)$ for the resulting numbers; the corresponding free ground terms have those depths. Let $\widehat K$ decode both numbers and then run $K$, rejecting either decoding failure.

#### Proposition 6.9 (Encoded composed checking).

The record and formula encodings have exact decoders, hence are injective in their respective sorts. Every observation of a record is recoverable from its single free ground term, and $$\widehat K(E(r),F(s))=K(r,s).$$ For a prefix of length $b$ with packed value $n$, $2^b\le n+1$ and $n+2\le 2^{b+1}$.

#### Proof.

The first packed bit is determined by parity, and removing it strictly decreases the remaining number. Induction gives unpacking after packing. Structural induction on a tree gives the prefix-parser round trip; requiring empty remaining input excludes trailing data. Constructor tags then give record and formula recovery by structural induction, including all premises and annotations. The free term of a given depth is unique. Recovery proves injectivity and observation preservation; the definition of $\widehat K$ gives checker agreement. Induction on the bit list proves the two bounds.

Thus materializing the unary term is exponential in the prefix length. The executable interface works on packed numbers: one checked separation record has 81 prefix bits but unary depth $2820815200072616987372202$. This is not a compression or performance theorem. Repeated subrecords remain stored in full. The Lean dependency report exposes classical choice in the size-bound proof; the executable decoder and checker do not use it.

#### Proposition 6.10 (Faithful model and an operational boundary).

There is a model of all 38 current logical clauses in which the composed record and formula codes retain their full decoded objects and encoded checking agrees with $K$. In that same model, the current finite congruence-preserving path relation cannot carry any encoded record to any encoded formula.

#### Proof.

Use the existing two-chain model, with forms $(n,\varepsilon)$ for $n\in\mathbb N$ and $\varepsilon\in\{0,1\}$, ground $(0,0)$, and application $(n,\varepsilon)\mapsto(n+1,\varepsilon)$. Congruence and simulation are equality; similarity is universal. The remaining parameter interpretations and all 38 clause checks are explicit in `FullAxiomModel.lean` \[16\]. The record and formula values are $(E(r),0)$ and $(F(s),0)$, exactly the interpretations of their free ground terms. Reading their first coordinates gives the required decoders and checker; values on the second chain are rejected.

The current preserving edge from $x$ to $y$ requires both $y=\operatorname{apply}(x)$ and congruence of $y$ with $x$. Here that would require $n+1=n$, so every preserving path is empty and has equal endpoints. The distinct record and formula envelopes give unequal values. No such path can therefore perform their direct transition.

The model is a compatibility witness, not a proof that all interpretations are faithful or that it captures the intended native semantics. Its decoders and checker are host functions on model values. The path obstruction concerns that direct transition in this specified model; it does not exclude a different native computation mechanism or ranked acceptance construction. Together with the collapsing model, it separates possible record retention from retention entailed by the clauses. Internal acceptance, source adequacy, arithmetic interpretation, transfinite realization, and coverage remain open.

# Why a truth stage cannot certify its own full truth

#### Theorem 7.1 (Undefinability at each stage).

For every $\alpha\le\theta$, there is no $L_\alpha$ formula $\tau(x)$ that defines $\mathsf{Tr}_\alpha$ in $M_\alpha$.

#### Proof.

The arithmetic part represents the syntactic substitution operation for the fixed effective language coding. Apply the diagonal lemma to $\neg\tau(x)$ to obtain an $L_\alpha$ sentence $\lambda$ satisfying $$M_\alpha\models\lambda\leftrightarrow\neg\tau(\ulcorner \lambda\urcorner).$$ If $\tau$ defined $\mathsf{Tr}_\alpha$, the same structure would satisfy $\tau(\ulcorner \lambda\urcorner)\leftrightarrow\lambda$. Together these force $\lambda\leftrightarrow\neg\lambda$, impossible in the classical two-valued structure. The diagonal lemma's syntactic construction uses only finitely many symbols of the candidate formula, so the countable predicate vocabulary causes no problem \[13\].

For $\alpha<\theta$, the next predicate $T_\alpha$ is not in $L_\alpha$, which is exactly why typed disquotation is compatible with this theorem. A sentence in $L_{\alpha+1}$ may apply $T_\alpha$ to its own code, but if that sentence uses $T_\alpha$, its code is outside $\operatorname{Sent}(L_\alpha)$ and the predicate returns false under our convention. Such an application is not a correct assertion of that sentence's own truth.

#### A precise positive answer.

The ordinal domain gives a definable copy of arithmetic; the metatheory gives its satisfaction relation; and the ordinal hierarchy provides successively richer languages in which earlier truth is available as a predicate. These together furnish the advertised sense of Tarski-definable arithmetic. The theorem rules out treating the union stage, the wrap map, or the name "ordinal" as an unrestricted self-truth mechanism.

The result is a semantic construction and assumes the resources of the metatheory. It supplies neither a recursively enumerable complete theory of arithmetic nor a proof of that metatheory's consistency. Allowing a source-specific similarity relation between a sentence and its negation would require a different logical semantics; it would not be a proof of the classical biconditionals used here.

# Computational companion

The accompanying Python library, `ordinatics` development version 0.2.0.dev0, implements a computable fragment of the construction and its algebraic interfaces.[^1] It uses exact integer coefficient tuples for ordinals below $\omega^\omega$. The operators `+` and `*` implement ordinary ordinal operations; `natural_add` and `natural_mul` implement the commutative polynomial operations. Conversion through `to_sympy` makes the representation map $j$ explicit. The resulting expressions can be used with SymPy symbolic calculus, matrices, and solvers, or converted to numerical functions for NumPy and SciPy. Numerical evaluation of a polynomial image is distinct from ordinal arithmetic.

The function `rational_function` validates and reduces exact rational functions. The functions `specialize` and `wrap` evaluate the reduced forms and raise a distinct pole exception when the reduced denominator vanishes at the evaluation point. Thus a removable singularity and a pole are observably different. A fixed logarithm branch is used for rational-power images. These routines realize the bounded value construction rather than a total evaluation of the whole field.

For semantics, the library supplies immutable arithmetic term and formula trees, static ordinal ranks, and an iterative evaluator. The constructors `Exists` and `ForAll` require a bound term and range over $0\le n<b$; the bound is evaluated in the outer assignment, and the quantifier binds its variable only in the body. A valid `Truth(beta, sentence)` node quotes a closed formula of rank at most `beta`; its language rank is $\beta+1$. The `rank` and `evaluate` functions enforce these conditions before evaluation. For example:

    from ordinatics import Add, Eq, Nat, Truth, ZERO, ONE, evaluate
    phi = Eq(Add(Nat(1), Nat(1)), Nat(2))
    assert evaluate(Truth(ZERO, phi), stage=ONE)

This quotation interface operates on explicit finite syntax trees. It is not an implementation of unrestricted numerical sentence codes. Invalid quotations are rejected before evaluation, whereas the mathematical truth sets defined above exclude malformed numerical codes by convention. The difference is part of the interface contract.

Ordinal labels enforce language membership. Evaluation of a valid quotation directly evaluates its closed quoted tree; it does not execute through preceding transfinite stages or construct their truth sets. Consequently the quotation nodes supply a typing discipline within this computable fragment, not an oracle for the full hierarchy.

Every quantifier iteration and tree traversal is charged against an explicit work-step budget. Exhaustion raises an exception rather than returning false. The budget bounds these steps, not the bit complexity of arbitrarily large integers or the execution time of external symbolic routines. The implementation does not construct $\mathsf{Tr}_\alpha$ for the full unbounded language. Its executable claims concern bounded formulas and exact algebraic examples; software tests do not replace the proofs of the semantic theorems.

# Contribution, limitations, and the next formal problem

The model joins three components with distinct contracts. The ordinal layer of Ordinatics supplies ordered values, finite arithmetic, and semantic stage indices. The bounded field layer supplies division, while wrap evaluation is restricted to functions regular at the chosen anchor. The satisfaction hierarchy supplies meaning for truth claims at specified language levels. None of these components obtains the other's authority merely by sharing a representation.

The dependency structure is deliberately revealing. The truth-hierarchy theorems require ordinal well-foundedness, syntax, and set-theoretic satisfaction, but they do not require the anchor $-1/2$, fractional powers, or a complex spiral. Thus the paper establishes a coherent interface *for* Ordinatics rather than proving that the value layer of Ordinatics is necessary for arithmetic truth. A stronger claim of necessity would require an additional theorem showing a semantic construction that depends essentially on that layer. No such theorem is asserted here.

The source's path-sensitive viewpoint has a concrete consequence nonetheless: semantic records should retain the formula, its language, its ordinal level, and its interpretation, even when numerical evaluations coincide. A verification record could therefore contain $(\alpha,\ulcorner \varphi\urcorner,s,v,p)$, where $v$ is a claimed satisfaction value and $p$ is a proof or evaluation certificate in a separately specified calculus. The existence theorem does not generate $p$. For an implementation, failure to obtain such a certificate must remain an unestablished claim, rather than being converted into either truth or falsity.

Four formal questions remain. First, a derivation from the $\square$ axioms needs a defined syntax, inference rules, and an interpretation theorem that actually produces the ordinal domain and the required recursion. Second, a complete treatment of Ordinatics needs a specified field or other algebra, a coherent root convention, and exact partiality conditions for wrap. Third, beyond the bounded evaluator, a proof-certificate checker needs a specified calculus and a soundness theorem relating accepted certificates to the displayed satisfaction clauses. Fourth, the intended fractal meta-representation must realize a named reflection progression, preserve the observations used after recursive reuse, and bind notation presentations to well-foundedness evidence. These questions are separable and permit bounded progress without claiming a universal truth algorithm.

The mathematically supportable thesis is therefore that ordinal structure can organize a typed foundation for arithmetic satisfaction while preserving both operational distinctions and semantic limits. The present reconstruction makes that thesis explicit. Its elementary obstructions and constructive model are offered as a technical foundation note; independent mathematical review and a broader novelty assessment remain appropriate before a stronger research claim.

# References {#references .unnumbered}

#### \[1\]

Alfred Tarski. The Semantic Conception of Truth and the Foundations of Semantics. *Philosophy and Phenomenological Research* 4(3), 341--376, 1944. [doi:10.2307/2102968](https://doi.org/10.2307/2102968). Author's article available as a [web transcription](https://www.jfsowa.com/logic/tarski.htm).

#### \[2\]

Volker Halbach. *Axiomatic Theories of Truth*. Second edition, Cambridge University Press, 2014. [doi:10.1017/CBO9781139696586](https://doi.org/10.1017/CBO9781139696586).

#### \[3\]

Lev D. Beklemishev and Fedor N. Pakhomov. Reflection Algebras and Conservation Results for Theories of Iterated Truth. *Annals of Pure and Applied Logic* 173(5), 103093, 2022. [doi:10.1016/j.apal.2022.103093](https://doi.org/10.1016/j.apal.2022.103093).

#### \[4\]

Graham E. Leigh. Reflecting on Truth. *IfCoLog Journal of Logics and their Applications* 3(4), 557--594, 2016. [Author-hosted journal issue](https://www.collegepublications.co.uk/downloads/ifcolog00008.pdf).

#### \[5\]

Solomon Feferman. Transfinite Recursive Progressions of Axiomatic Theories. *The Journal of Symbolic Logic* 27(3), 259--316, 1962. [doi:10.2307/2964649](https://doi.org/10.2307/2964649).

#### \[6\]

Fedor Pakhomov, Michael Rathjen, and Dino Rossegger. Feferman's Completeness Theorem. [arXiv:2405.09275 \[math.LO\]](https://doi.org/10.48550/arXiv.2405.09275), 2024; published in *Bulletin of Symbolic Logic* 31(3), 462--487, 2025, [doi:10.1017/bsl.2025.2](https://doi.org/10.1017/bsl.2025.2).

#### \[7\]

Solomon Feferman. Turing's Thesis. *Notices of the American Mathematical Society* 53(10), 1200--1205, 2006. [Author-hosted article](https://math.stanford.edu/~feferman/papers/turing.pdf).

#### \[8\]

Bryan Ford. Computable Quantification in Reflective Grounded Arithmetic. [arXiv:2607.25533 \[math.LO\]](https://doi.org/10.48550/arXiv.2607.25533), 2026.

#### \[9\]

Bryan Ford. Internalized Truth in Reflective Grounded Arithmetic. [arXiv:2608.16140 \[math.LO\]](https://doi.org/10.48550/arXiv.2608.16140), 2026.

#### \[10\]

James Brotherston and Alex Simpson. Sequent Calculi for Induction and Infinite Descent. *Journal of Logic and Computation* 21(6), 1177--1216, 2011. [doi:10.1093/logcom/exq052](https://doi.org/10.1093/logcom/exq052).

#### \[11\]

Anupam Das. On the Logical Complexity of Cyclic Arithmetic. *Logical Methods in Computer Science* 16(1:1), 1--39, 2020. [doi:10.23638/LMCS-16(1:1)2020](https://doi.org/10.23638/LMCS-16(1:1)2020).

#### \[12\]

Lorenz Halbeisen. The Axioms of Set Theory ZFC, Chapter 13, especially Theorem 13.3 and the ordinal arithmetic section. [Author-hosted chapter](https://people.math.ethz.ch/~halorenz/4students/LogikGT/Ch13.pdf), accessed September 6, 2026.

#### \[13\]

Michael Beeson. Lecture 13: The First Incompleteness Theorem. Stanford logic lecture slides, especially the self-reference lemma and undefinability discussion. [Author-hosted slides](https://www.michaelbeeson.com/teaching/StanfordLogic/Lecture13Slides.pdf), accessed September 6, 2026.

#### \[14\]

The Stacks Project Authors. Section 10.9: Localization. [Tag 00CM](https://stacks.math.columbia.edu/tag/00CM), accessed September 7, 2026.

#### \[15\]

National Institute of Standards and Technology. Digital Library of Mathematical Functions, Section 4.2: Definitions, Logarithm, Exponential, Powers. [DLMF Section 4.2](https://dlmf.nist.gov/4.2), accessed September 7, 2026.

#### \[16\]

Tyler Roost. *Hypermath: Fractal meta-representation and Gödelian completeness research target*. Development source and proof audit at commit [34c9c99345bb3cdeac7be9a67713d9aa0c99d6da](https://github.com/TimeLordRaps/hypermath/tree/34c9c99345bb3cdeac7be9a67713d9aa0c99d6da), 2026. The repository records open proof obligations and countermodels; it is not an independent completeness certificate.

#### \[17\]

Tyler Roost. Unpublished working notes on Ordinatics: *Ordinatics* (Chapter 48), *The Wrap Operation W* (Chapter 50), *The Four-Level Ordinate Hierarchy* (Chapter 97), and *Dimensional Transition Operators* (Chapter 98), with accompanying ordinal-extension specifications. Manuscripts consulted September 6, 2026; Chapters 97--98 dated August 6, 2026. These are sources of the research proposal, not independently validated proof certificates. All definitions required for the present results are given in this paper.

[^1]: <https://github.com/TimeLordRaps/ordinatics>
