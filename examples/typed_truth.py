"""Finite typed quotations; this does not decide unbounded arithmetic truth."""

from ordinatics.ordinals import ONE, ZERO, Ordinal
from ordinatics.semantics import Add, Eq, ForAll, Lt, Nat, Truth, Var, evaluate, rank


def main() -> None:
    arithmetic = Eq(Add(Nat(2), Nat(2)), Nat(4))
    truth_at_zero = Truth(ZERO, arithmetic)
    truth_at_one = Truth(ONE, truth_at_zero)
    bounded = ForAll("n", Nat(10), Lt(Var("n"), Nat(10)))

    for label, sentence, stage in (
        ("T_0(2 + 2 = 4)", truth_at_zero, ONE),
        ("T_1(T_0(2 + 2 = 4))", truth_at_one, Ordinal((2,))),
        ("for all n < 10, n < 10", bounded, ZERO),
    ):
        print(f"{label}: rank={rank(sentence)}, value={evaluate(sentence, stage=stage)}")


if __name__ == "__main__":
    main()
