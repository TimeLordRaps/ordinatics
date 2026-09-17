# Ordinal Arithmetic: An Ordinal-First Metalanguage Approach to Definable Arithmetic Truth

Tyler Roost

Preprint, version 1.0 --- September 7, 2026

## Abstract

Ordinatics proposes an arithmetic of ordinal forms with division and a finite-valued wrap map, while retaining distinctions between construction paths and numerical outcomes. We give a bounded mathematical reconstruction directed at the definition of arithmetic truth in an ordinal framework. Finite ordinals supply the arithmetic domain, and ordinals below $\omega^\omega$ index a hierarchy of languages whose truth predicates apply to earlier languages. In an explicit set-theoretic metatheory, the hierarchy has a unique satisfaction interpretation and preserves arithmetic truth under passage to later stages. Each stage nevertheless lacks a definition of its own full truth predicate. We also construct a rational-function model for a value layer of Ordinatics with a partial specialization $W(X)=-1/2$, and prove why neither ordinary ordinal addition nor all nonzero field elements can pass through that specialization unchanged. These results separate ordinal order, algebraic evaluation, and semantic authority. The contribution is an explicit interface and dependency analysis for the Ordinatics proposal, rather than a new undefinability theorem or a derivation of arithmetic truth from numerical compression alone.

**Keywords:** Ordinatics; ordinal arithmetic; satisfaction; ramified truth; partial specialization; derivation paths.

# The foundational question

What would it mean to make ordinal arithmetic the underlying foundation of a Tarski-definable arithmetic? The phrase needs a language and a domain of definability. In this paper it means that the truth and satisfaction relations for an arithmetic object language are definable in a specified richer framework, with explicit ordinal bounds on the languages to which each truth predicate applies. It does not mean decidability of arithmetic or an unrestricted truth predicate definable inside its own language.

Here "ordinal-first" refers to the arithmetic domain and the ordering of semantic dependencies. The ambient metalanguage is the set theory specified below; the paper does not assert definability of arithmetic truth in the ordinal-arithmetic structure alone.

We use *Ordinatics* as the name of the overall framework. The motivating notes distinguish a layer of ordinary ordinal operations, an intended extension admitting reciprocals and fractional powers, and a further complex-valued extension \[7\]. We retain these as distinct layers within Ordinatics. They also distinguish derivation-path identity, written $=$ in those notes, from outcome congruence $\equiv$ and continuation similarity $\sim$. This separation suggests that an expression should retain more information than its numerical image. We preserve that design question while making the mathematical interpretation explicit.

Three roles of ordinals must be distinguished. First, finite ordinals carry ordinary arithmetic. Second, transfinite ordinals organize the dependencies of semantic definitions. Third, ordinal expressions can motivate algebraic expressions that admit division. These roles can coexist in a typed framework, but their operations need not agree. An ordinal rank is not automatically a field value, and a field value is not a truth predicate.

The established background is the definition of truth through satisfaction and the restriction on truth definitions for semantically closed languages \[1\]. Transfinite progressions also have a substantial prior history; Feferman's work studies progressions of axiomatic theories \[2\]. Our construction below is a semantic hierarchy, not an identification with any particular progression of reflection principles. The elementary results are proved here to make the proposed interface independently assessable. No priority claim is made for ordinal-indexed truth hierarchies, polynomial fields, or localization.

#### Ambient assumptions.

We work in ordinary classical mathematics formalizable in Zermelo--Fraenkel set theory with the Axiom of Choice, abbreviated ZFC. Its operational role is to supply sets, finite syntax, and transfinite recursion, not a numerical unit. All quantities below are mathematical objects with no physical dimension. The use of this metatheory is explicit: the paper does not derive its set existence assumptions from the source notes' $\square$ ground-and-term-former. A faithful internal derivation in that system remains a separate research obligation.

# Ordinal arithmetic without a change of operations

Let $\omega$ be the least infinite ordinal. Write $+_o$ and $\cdot_o$ for ordinary ordinal addition and multiplication, defined recursively in the right argument. In particular, $$\begin{align*}
\alpha+_o0&=\alpha,&\alpha+_o(\beta+1)&=(\alpha+_o\beta)+1,\\
\alpha\cdot_o0&=0,&\alpha\cdot_o(\beta+1)&=(\alpha\cdot_o\beta)+_o\alpha.
\end{align*}$$ At a nonzero limit, take the supremum of the earlier values. This is the standard ordinal recursion construction \[3\]. It gives $$1+_o\omega=\omega,\qquad \omega+_o1>\omega,
\qquad 2\cdot_o\omega=\omega,\qquad \omega\cdot_o2=\omega+_o\omega.$$ Thus even the expression "twice an ordinal" needs an operand order.

#### Proposition 2.1 (Absorption obstructs a unital additive field interpretation).

Suppose a domain contains $1,\omega$ and $1+_o\omega=\omega$. There is no map $f$ into the additive group of a nontrivial field such that $f(1)=1$ and $f(\alpha+_o\beta)=f(\alpha)+f(\beta)$ on these inputs.

#### Proof.

The absorption equation would imply $1+f(\omega)=f(\omega)$. Cancellation gives $1=0$, contradicting nontriviality.

This obstruction does not depend on injectivity or on the field being Archimedean. Passing to an ordered field with infinite elements does not repair it. One may introduce new field operations on representations of ordinals, but that is a change of operations and must be marked as such.

For a concrete set-sized ordinal domain, fix $$\theta=\omega^\omega,\qquad \mathcal O=\{\alpha : \alpha<\theta\},
\qquad \mathcal A=(\mathcal O,0,1,\omega,<,+_o,\cdot_o).$$ Every element has a unique finite ordinal polynomial representation $$\alpha=\omega^k a_k+_o\cdots+_o\omega a_1+_o a_0,
\quad a_j\in\mathbb N,$$ where coefficients multiply on the right and the leading coefficient is nonzero unless $\alpha=0$. Finite addition and multiplication of these ordinals remain below $\theta$: the highest exponent of a sum is at most the maximum of the input exponents, and that of a nonzero product is at most their sum. This representation is the restricted Cantor normal form. It gives computable finite codes and a computable comparison relation for the ranks used below. The bound is a convenient concrete choice, not a proposed ultimate ordinal of the theory.

#### Proposition 2.2 (Arithmetic as a definable finite-ordinal part).

In $\mathcal A$, the formula $x<\omega$ defines a domain whose induced $0,1,+_o,\cdot_o$ structure is the standard arithmetic structure $(\mathbb N,0,1,+,\cdot)$.

#### Proof.

The ordinals below $\omega$ are exactly the finite ordinals. The displayed recursions restrict to the usual addition and multiplication recursions on them. Relativize every arithmetic quantifier to $x<\omega$. Induction on terms and formulas shows that this translation preserves satisfaction.

Consequently an ordinal foundation retains arithmetic's capacity to encode syntax. Replacing natural-number notation with ordinal notation does not by itself remove diagonalization. The proposition establishes a definable arithmetic domain; it does not establish a definable truth predicate in $\mathcal A$.

# A bounded value layer for Ordinatics

The source wrap anchor $W(\omega)=-1/2$ is useful as a proposed numerical evaluation. To interpret it coherently, introduce an indeterminate $X$ distinct from the ordinal $\omega$. Let $$K=\mathbb Q(X),\qquad c=-\tfrac12,
\qquad S=\{q\in\mathbb Q[X]:q(c)\ne0\},\qquad R=S^{-1}\mathbb Q[X].$$ Here $K$ is the field of rational functions. The ring $R$ consists of rational functions admitting a representation with denominator nonzero at $c$; this is the standard localization construction \[5\]. Define $$W:R\longrightarrow\mathbb Q,\qquad W(p/q)=p(c)/q(c).$$ We call $K$ a *bounded value model of Ordinatics*: it realizes division in a value layer motivated by ordinal forms. It is not asserted to be the full Subreal type of the notes, an algebraically closed field, or a model of every $\square$ axiom.

#### Theorem 3.1 (Scope of wrap specialization).

The map $W$ is a well-defined surjective unital ring homomorphism on $R$. Its kernel is $(X-c)R$. It cannot extend to a unital field homomorphism $K\to\mathbb Q$. An element $r\in R$ is a unit of $R$ (has a multiplicative inverse in $R$) if and only if $W(r)\ne0$.

#### Proof.

If $p/q=p'/q'$ then $pq'=p'q$; evaluating at $c$ and dividing by the nonzero denominators proves well-definedness. Evaluation respects sums and products and fixes rational constants, which also proves surjectivity. A polynomial vanishes at $c$ exactly when it is divisible by $X-c$, giving the kernel assertion. In $K$, the nonzero element $X-c$ has an inverse. An extension would send $(X-c)(X-c)^{-1}=1$ to $0\cdot W((X-c)^{-1})=1$, a contradiction. Finally, if $r=p/q$ and $W(r)\ne0$, then $p(c)\ne0$ and $q/p\in R$. Conversely, an inverse in $R$ would give $W(r)W(r^{-1})=1$.

This construction recovers $W(X^n)=(-1/2)^n$ for every integer $n$, including $W(X^{-1})=-2$. It also exposes a necessary limitation: $2X+1$ is a nonzero field element with wrap value zero, so its inverse has no wrap value under this specialization. Undefined evaluation is distinct from zero evaluation.

There is a faithful *representation map* $$j\colon \mathcal O\longrightarrow\mathbb N[X]\subset K,\qquad
j(\omega^k a_k+_o\cdots+_o a_0)=a_kX^k+\cdots+a_0.$$ It is a bijection onto polynomials with nonnegative integer coefficients, by uniqueness of the normal form. Pulling polynomial addition and multiplication back along $j$ gives commutative operations $\oplus,\otimes$ on $\mathcal O$. By construction, $$j(\alpha\oplus\beta)=j(\alpha)+j(\beta),\qquad
j(\alpha\otimes\beta)=j(\alpha)j(\beta).$$ They agree with ordinary arithmetic on finite ordinals, but $1\oplus\omega=\omega+_o1$ whereas $1+_o\omega=\omega$. These are the natural ordinal operations on this restricted domain; their distinction from ordinary ordinal operations is essential. The field is generated by $j(\mathcal O)$ over $\mathbb Q$, but $j$ is not an embedding for $+_o,\cdot_o$.

## Fractional powers and branch data

If fractional monomials are added, choose a coherent branch explicitly. For instance, with $\ell=-\log 2+i\pi$, the map $$\chi:(\mathbb Q,+)\longrightarrow(\mathbb C\setminus\{0\},\cdot),
\qquad \chi(r)=\exp(r\ell)$$ satisfies $\chi(r+s)=\chi(r)\chi(s)$ and $\chi(1)=c$. However, $\chi(1/3)=2^{-1/3}e^{i\pi/3}$ is not the real cube root $-2^{-1/3}$. Choosing a real cube root at $1/3$ and the principal value $2^{-1/6}e^{i\pi/6}$ at $1/6$ violates $\chi(1/3)=\chi(1/6)^2$. A mixed root convention is therefore not a single multiplicative character. Also, a collection of nonzero monomial values is not itself a field: it does not contain zero, let alone automatically supply all sums.

For complex $z$, the same expression $\Phi(z)=\exp(\ell z)$ is surjective onto $\mathbb C\setminus\{0\}$, but $$\Phi(z)=\Phi(z')\quad\Longleftrightarrow\quad
z-z'\in\frac{2\pi i}{\ell}\mathbb Z.$$ This follows from the kernel of the complex exponential. Thus $\Phi$ induces a bijection from the quotient by that lattice onto $\mathbb C\setminus\{0\}$. Restricting its domain to the half-open strip $-\pi<\operatorname{Im}(\ell z)\le\pi$ also gives a set bijection onto $\mathbb C\setminus\{0\}$, but its inverse is discontinuous across the negative real axis. An analytic logarithm branch instead uses a slit codomain, for example $\mathbb C\setminus(-\infty,0]$ \[6\]. A numerical image generally does not identify its source expression. Neither the real-root convention nor complex injectivity is needed for the truth construction below.

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

Let $L_0=\{0,1,+,\cdot,<\}$ be the first-order language of arithmetic, with equality. Fix an injective effective coding into $\mathbb N$ of finite terms and formulas, including canonical finite-tuple codes for ordinal polynomial indices below $\theta$. Choose the coding so that parsing, numeral formation, and capture-avoiding substitution are computable, as with the usual coding of finite strings over an effectively indexed vocabulary. The symbol $T_\beta$ is a unary predicate for each $\beta<\theta$. For $\alpha\le\theta$, put $$L_\alpha=L_0\cup\{T_\beta : \beta<\alpha\}.$$ The predicate $T_\alpha$ will express truth for *sentences of $L_\alpha$*; it first occurs in $L_{\alpha+1}$ when that language is within the chosen range. At $\theta$ we construct the truth set externally without adding its symbol to $L_\theta$.

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

# Why a truth stage cannot certify its own full truth

#### Theorem 6.1 (Undefinability at each stage).

For every $\alpha\le\theta$, there is no $L_\alpha$ formula $\tau(x)$ that defines $\mathsf{Tr}_\alpha$ in $M_\alpha$.

#### Proof.

The arithmetic part represents the syntactic substitution operation for the fixed effective language coding. Apply the diagonal lemma to $\neg\tau(x)$ to obtain an $L_\alpha$ sentence $\lambda$ satisfying $$M_\alpha\models\lambda\leftrightarrow\neg\tau(\ulcorner \lambda\urcorner).$$ If $\tau$ defined $\mathsf{Tr}_\alpha$, the same structure would satisfy $\tau(\ulcorner \lambda\urcorner)\leftrightarrow\lambda$. Together these force $\lambda\leftrightarrow\neg\lambda$, impossible in the classical two-valued structure. The diagonal lemma's syntactic construction uses only finitely many symbols of the candidate formula, so the countable predicate vocabulary causes no problem \[4\].

For $\alpha<\theta$, the next predicate $T_\alpha$ is not in $L_\alpha$, which is exactly why typed disquotation is compatible with this theorem. A sentence in $L_{\alpha+1}$ may apply $T_\alpha$ to its own code, but if that sentence uses $T_\alpha$, its code is outside $\operatorname{Sent}(L_\alpha)$ and the predicate returns false under our convention. Such an application is not a correct assertion of that sentence's own truth.

#### A precise positive answer.

The ordinal domain gives a definable copy of arithmetic; the metatheory gives its satisfaction relation; and the ordinal hierarchy provides successively richer languages in which earlier truth is available as a predicate. These together furnish the advertised sense of Tarski-definable arithmetic. The theorem rules out treating the union stage, the wrap map, or the name "ordinal" as an unrestricted self-truth mechanism.

The result is a semantic construction and assumes the resources of the metatheory. It supplies neither a recursively enumerable complete theory of arithmetic nor a proof of that metatheory's consistency. Allowing a source-specific similarity relation between a sentence and its negation would require a different logical semantics; it would not be a proof of the classical biconditionals used here.

# Computational companion

The accompanying Python library, `ordinatics` version 0.1.0, implements a computable fragment of the construction and its algebraic interfaces.[^1] It uses exact integer coefficient tuples for ordinals below $\omega^\omega$. The operators `+` and `*` implement ordinary ordinal operations; `natural_add` and `natural_mul` implement the commutative polynomial operations. Conversion through `to_sympy` makes the representation map $j$ explicit. The resulting expressions can be used with SymPy symbolic calculus, matrices, and solvers, or converted to numerical functions for NumPy and SciPy. Numerical evaluation of a polynomial image is distinct from ordinal arithmetic.

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

Three formal questions remain. First, a derivation from the $\square$ axioms needs a defined syntax, inference rules, and an interpretation theorem that actually produces the ordinal domain and the required recursion. Second, a complete treatment of Ordinatics needs a specified field or other algebra, a coherent root convention, and exact partiality conditions for wrap. Third, beyond the bounded evaluator, a proof-certificate checker needs a specified calculus and a soundness theorem relating accepted certificates to the displayed satisfaction clauses. These questions are separable and permit bounded progress without claiming a universal truth algorithm.

The mathematically supportable thesis is therefore that ordinal structure can organize a typed foundation for arithmetic satisfaction while preserving both operational distinctions and semantic limits. The present reconstruction makes that thesis explicit. Its elementary obstructions and constructive model are offered as a technical foundation note; independent mathematical review and a broader novelty assessment remain appropriate before a stronger research claim.

# References {#references .unnumbered}

#### \[1\]

Alfred Tarski. The Semantic Conception of Truth and the Foundations of Semantics. *Philosophy and Phenomenological Research* 4(3), 341--376, 1944. [doi:10.2307/2102968](https://doi.org/10.2307/2102968). Author's article available as a [web transcription](https://www.jfsowa.com/logic/tarski.htm).

#### \[2\]

Solomon Feferman. Transfinite Recursive Progressions of Axiomatic Theories. *The Journal of Symbolic Logic* 27(3), 259--316, 1962. [doi:10.2307/2964649](https://doi.org/10.2307/2964649).

#### \[3\]

Lorenz Halbeisen. The Axioms of Set Theory ZFC, Chapter 13, especially Theorem 13.3 and the ordinal arithmetic section. [Author-hosted chapter](https://people.math.ethz.ch/~halorenz/4students/LogikGT/Ch13.pdf), accessed September 6, 2026.

#### \[4\]

Michael Beeson. Lecture 13: The First Incompleteness Theorem. Stanford logic lecture slides, especially the self-reference lemma and undefinability discussion. [Author-hosted slides](https://www.michaelbeeson.com/teaching/StanfordLogic/Lecture13Slides.pdf), accessed September 6, 2026.

#### \[5\]

The Stacks Project Authors. *The Stacks Project*, Section 10.9: Localization (Tag 00CM). <https://stacks.math.columbia.edu/tag/00CM>, accessed September 7, 2026.

#### \[6\]

National Institute of Standards and Technology. *Digital Library of Mathematical Functions*, Section 4.2: Logarithm, Exponential, Powers. <https://dlmf.nist.gov/4.2>, accessed September 7, 2026.

#### \[7\]

Tyler Roost. Unpublished working notes on Ordinatics: *Ordinatics* (Chapter 48), *The Wrap Operation W* (Chapter 50), *The Four-Level Ordinate Hierarchy* (Chapter 97), and *Dimensional Transition Operators* (Chapter 98), with accompanying ordinal-extension specifications. Manuscripts consulted September 6, 2026; Chapters 97--98 dated August 6, 2026. These are sources of the research proposal, not independently validated proof certificates. All definitions required for the present results are given in this paper.

[^1]: <https://github.com/TimeLordRaps/ordinatics>
