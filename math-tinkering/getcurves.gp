/*
This program finds suitable elliptic curves to construct
trapdoor projection maps to two cyclic subgroups contained within
the N-torsion group of said elliptic curve.

Author		: Thomas Pluck
Last Updated	: 11:41 18/06/2021 (CEST)
*/

/*
Compute a suitable D and N according to [1] and [2],
for shorthand we refer to Q(sqrt(-D)) as K.

D must satisfy the following properties:
1) -D mod 4 = 0 or 1
2) If p^n|D and p odd, n == 1

N must satisfy the following properties:
1) If p|N then p!|K
2) If p|N then p must be split in K/Q
3) gcd(N,2D) == 1

We use a few of facts about quadratic fields:

1) K's discriminant is -D if -D % 4 == 1 and -4D otherwise.
2) 2 is split in K/Q if d % 8 = 1
3) odd p is split in K/Q if (d|p) = 1
*/

is_split(p,d) =
{
	if(p == 2,
		if(d % 8, return(1), return(0)));
	
	if(kronecker(d,p) == 1, return(1), return(0));
}

get_params(n,upper) =
{
	\\ Random D
	my(r=1)
	for(t=0, n,
		while(-D % 4 || -D % 4 - 1 || inList(factor(D),r),
			r = randomprime([2,upper]);
			if(inList(factor(D),r),0,D=D*randomprime([2,upper])));
	
	\\ Random N
	my(discprimes = factor(if(-D % 4 == 1, -D, 4*-D)));
	
	N = 1;
	for(t=0, n,
		while(!is_split(r,-D) || inList(discprimes,r),
			r = randomprime([3,upper]));
		N = N*r);
	
	\\ Return [N,D]	
	[N,D];
}

/*
This algorithm is the modified BGN-Setup from [1] where
an appropriate prime q is found and N,D,q are passed to
the CM-method [3].
*/

bgn_cm(N,D) =
{
	\\ Find appropriate prime
	k = 1;
	while(!isprime(1+D*k^2*N^2),k++);
	q = 1 + D*k^2*N^2;

	\\ Find and solve corresponding Hilbert Class Polynomial
	disc = if(-D % 4 == 1, -D, 4*-D);
	hilb = polclass(D);
	j0 = polrootsmod(hilb,q)[1];
	
	\\ Generate elliptic curve, check for correct properties
	e = ellfromj(j0);
	E = ellinit(ec,q);
	if(ellcard(E) == q-1,return(E),return(elltwist(E,q)));
}

/*
Now that an appropriate curve has been selected, we are now in a
position to derive the projection maps to the cyclic subgroups.

Explicitly these are given as (s+sig)/2s and -(sig-s)/2s where,
s = sqrt(-D mod N) and sig is the action of sqrt(-D) ie. a map
which if applied twice generates the action of -D.

The specific algorithm used to compute the latter is borrowed from [4].
*/

gen_keys(N,D,E) =
{
	s = sqrt(Mod(-D,N))
	
}
