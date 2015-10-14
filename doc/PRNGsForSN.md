# Goal:
Want to draw ordered pre-specified length (say ~20) list of random numbers for
each object in an ordered list of objects
- Such that we can access the list of random numbers associated with the ith object quickly
- with small (preferably no) storage involved
- when the number of objects is very large (N ~ 2e10)
- While we can assume some spatial properties of the object indices, we would like this to be either independent of the details of how the object indices are assigned, or at least  easily extensible to other procedures of object index assignments.

To clarify, consider an example:
object  randomNumbers ~U(0,1)

- 0        (x00, x01, x02, x03, ..., x020)
- 1        (x10, x11, x12, x13, ..., x120)
....
- i        (xi0, xi1, xi2, xi3, ..., xi20)
...
- N        (xN0, xN1, xN2, xN3, ..., xN20)

We want an approach where we can find the random (xi0, xi1, xi3,...xi20)
easily without storing them, irrespective of the value of i.

I tried to build this example in a generic language for everyone, but more specifically what is of interest right now are galaxies (corresponding to objects above) in the LSST simulation database. These are indexed by a unique ID
called galtileID, which is currently built from an ID identifying the tile of space containing the location of the galaxy, and the id corresponding particular galaxy in a base catalog.

## Approach 1: Use the index of the objects as seeds.
In the above example the index is the first column (object). You could imagine seeding the random number generator with these index values, and draw the 20 random numbers corresponding to these objects.

### pros:

- Easy to obtain the random numbers associated with any object very quickly
- No storage

### cons:

- No guarantees on getting independent randoms numbers, though if the seed pool is large compared the number of objects, this is probably safe for the most part. This is the common problem with storing seeds rather than the states in a sequence.
- With the current python PRNG based on a 32 bit Mersenne Twister, the number of seeds (limited to 32 bit integers) is much smaller than the number of  objects we are interested in. This particular problem can be solved by moving to an algorithm that involves a 64 bit seed.

## Approach 2: Store the states of the PRNGs / store the random numbers themselves
At any time, the PRNG is completely described by a state which is a list of integers. This amounts to adding columns
on the first example holding either the list of random numbers, or the list of integers to specify the state.

 object   PNRG-state
- 53       state1
- 27       state2
- 23       state3
- 192      state4

at a particular object, read the PRNG state, and draw the
random numbers from there, and this is very fast.

### pros:

- Easy to obtain random numbers associated with any object, if the state is stored
- Uses random number generators correctly, all the generated numbers should follow all the guarantees from the PRNG algorithm.

### cons:

- Storage of states is too expensive. For the default numpy.random PRNG this is 624 * 4 bytes per object, and we have ~4e10 objects. This can be partially addressed if the state space is small, (for example there are PRNGs with large periods, which have a state specified by a much smaller number of integers), but is unlikely to be less than 8 bytes per object.

## Approach 3: Jumpaheads:
Start with a particular seed, and imagine running through the list of objects using the object index to
define the position of the object in the sequence during an assignment phase. Later on, to obtain the same set of randoms for a particular object, all we need is the initial
seed and the index of the object.

### pros:

- Uses random number generators correctly, all the generated numbers should follow all the guarantees from the PRNG algorithm.
- No Storage involved

### cons:

- Slow: In the slowest way always possible, to obtain the set of randoms associated with object index i, this amounts to starting with the random seed and drawing the first i -1
randoms to get to the state corresponding to state i. If, we have closeby and ordered indexes for every use-case we will work on, and have large index values, all of which are true for us, this process will be very slow.
However, it is possible to have more efficient jumpahead algorithms that simply take you to the state of the PRNG corresponding to position 'i' in the sequence for the PRNG with a particular seed.

## Approach 4: Storing states on a smaller number of objects and using jumpaheads

If we understand that all use-cases that we are concerned only involve sets of object ids, (for example because we will be doing spatial queries of sizes smaller than some limit). we could combine jumpaheads with storing states on one object in each of these sets.

## Approach 5: Dynamic Seed creation + approach 1
