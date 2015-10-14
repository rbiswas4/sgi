# Goal:
Want to draw ordered pre-specified length (say ~20) list of random numbers for
each object in an ordered list of objects
- Such that we can access the list of random numbers associated with the ith object quickly
- with small (preferably no) storage involved
- when the number of objects is very large (N ~ 2e10)

To clarify, consider an example:
object  randomNumbers ~U(0,1)
0        (x00, x01, x02, x03, ..., x020)
1        (x10, x11, x12, x13, ..., x120)
....
i        (xi0, xi1, xi2, xi3, ..., xi20)
...
N        (xN0, xN1, xN2, xN3, ..., xN20)

We want an approach where we can find the random (xi0, xi1, xi3,...xi20)
easily without storing them, irrespective of the location of i.
## Approach 1:
Use the index of the objects as seeds 
Problems with using the galtileIds to seed a PNRG

- The main mundane problem we cannot get around is that our galtileId values exceed the size of the maximum
 seed allowed on the PRNG in python (a 32 bit mersenne twister). This maximum value is set by this 32 bit character
of the PRNG and is therefore 2^32 -1= 4294967295 ~ 4.2 e9  while the number of galaxies is of the order of
2.0 e7 * 2.5e3 ~5. e10.  So, we cannot seed the PNRG with a galtileID. (Incidentally, I also better understand something
we have discussed but though irrelevant why we are not supposed to use different IDs as seeds. and on both counts  I think we need to change methods)

## Options
- We have options of moving to a different PNRG method: like the 64 bit Mersenne Twister, where the limit on the seed will  be 2^64 -1  or some other method which allows a larger seed. This has the practical difficulty of having to lose the nice
functionalities numpy is providing us right now,  since numpy does not provide a way to switch generators. One way to
get some of the nice functionalities without implementing out own generator is to use Boost which supplies a number of
PNRG implementations. I also think that  it is simply better to actually do the random number generation in the way these
generators are meant to be used, even if we change the PNRG.
- So, I think we should try to record the state of the PNRG, whether or not we change the PNRG .

 This  would mean starting off with a single seed of our choice, going through our fields one galaxy at a time and drawing a certain number
of random numbers for each galaxy and recording the state of the PNRG as soon as we move to a new galaxy. Schematically,
we are talking about storing

galtileID  PNRG-state
53           <state1>
27           <state2>
23           <state3>
192         <state4>

In that case, we will be reproducible again, we go to a galaxy later on, and read the galtileID, say it is 23. We look up the state
from this table and find it is <state3> and then we take a PNRG and set its state to <state3> and we can draw the same set of
random numbers associated with the galaxy. Python (numpy) provides such `set_state`, and `get_state` functionality, and the
state in question is an object. To serialize, we have two alternatives:
 - need to store the parameters required to instantiate that object.
 - We can store the starting seed and an integer index that specifies the the position in the sequence  for the galaxy, so

galtileID  position in sequence
53           1
27           2
23           3
192         4

For the first method, the problem is specifying the state space for the Mersenne Twister: This has a size of 624 * 32 bits per state.
For our galaxies, this comes to 5 e10 * 2.5 e3 ~ 125 TB. We can be helped be a different PNRG with a smaller state space, and
we can do with a period > 2**32 (like the 2**64 periods should be fine for us), rather than the huge period of the Mersenne Twister.
At the very least though, this would mean a 64 bit integer for every galaxy ~ 5e10 * 8 bytes  = 400 GB, but the state space could
be larger.

Second Method:  If we store the position on the sequence we can do this in 4e10 * 64 bytes = 400 GB. But while assigning such
random numbers is easy, it is a lot harder to look up the random numbers during application. The typical problem will be that during
an application we will be looking up galaxies

position in sequence

2343
7265
374
18884

In the dumb, brute-force way this means we start with a seed .... draw 2342 random numbers, and
get to the state we want for the first galaxy. Then we draw 7265 - (2343 + num_randoms_perGal)
to get to the state for the second galaxy. Then we reseed and go to 374 etc. So slow.

Finally, we could do away with this cost of storage, if we used the galtileId as the position in the sequence. However, since the
galtileIDs are not sequential, what we will have to do is go through the above problem even during assignment.

The way to get around this is by asking if there are fast methods for composing the changes to the state of the random number
by the position in the sequence. This seems to be called 'Jumpahead' in the literature.  So, what we seem to need is :

1. A PNRG with a period of say 2**64
2. A PNRG with a fast Jumpahead algorithm
3. If the jumpahead is not easy, we could think of one with a small state space.
