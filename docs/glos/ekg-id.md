# EKG/ID

An EKG/ID is an Enterprise Knowledge Graph Identifier that has the form of a number.

At higher levels of maturity for your overall EKG Platform Architecture you may wish
to switch over from using [EKG/IRIs](ekg-iri.md) for all your EKG identifiers to
EKG/IDs in order to decouple the primary identifiers for any given "thing" in your
Enterprise Knowledge Graph from their DNS host or domain name as that is encoded
in each HTTP URL today.

In other words, in the various backend data-stores of your EKG you then no longer
use HTTP URLs as the identifier for any given thing but numbers (either large
random numbers or large hash numbers, signed or not signed).
