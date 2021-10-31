package main

import (
	"fmt"
	_ "math"
	"math/rand"
	"time"
	
	"github.com/montanaflynn/stats"
	"github.com/ldsec/lattigo/ckks"
	"github.com/ldsec/lattigo/rlwe"
)

func initializeScheme() (ckks.Encryptor, ckks.Decryptor, ckks.Encoder, ckks.Evaluator, ckks.Parameters) {

	var err error
	
	//params, err := ckks.NewParametersFromLiteral(ckks.ParametersLiteral{
	//	LogN:     14,
	//	LogQ:     []int{55, 40, 40, 40, 40, 40, 40, 40},
	//	LogP:     []int{45, 45},
	//	Sigma:    rlwe.DefaultSigma,
	//	LogSlots: 0,
	//	Scale:    float64(1 << 40),
	//})
	
	// Using recommended post-quantum 128-bit secure parameters
	params, err := ckks.NewParametersFromLiteral(ckks.PN12QP109)
	if err != nil {
		panic(err)
	}

	kgen := ckks.NewKeyGenerator(params)

	sk := kgen.GenSecretKey()
	
	pk := kgen.GenPublicKey(sk)

	rlk := kgen.GenRelinearizationKey(sk, 2)

	encryptor := ckks.NewEncryptor(params, pk)

	decryptor := ckks.NewDecryptor(params, sk)

	encoder := ckks.NewEncoder(params)

	evaluator := ckks.NewEvaluator(params, rlwe.EvaluationKey{Rlk: rlk})
	
	return encryptor,decryptor,encoder,evaluator,params
}

// Works by fitting shifted taylor sine which fits much better
func cosine(eval ckks.Evaluator, ctIn *ckks.Ciphertext) (ctOut *ckks.Ciphertext) {

	var err error
	
		coeffs := []complex128{
		complex(1.0, 0),
		complex(0.0, 0),
		complex(-1.0/2, 0),
		complex(0.0, 0),
		complex(1.0/24, 0),
		complex(0.0, 0),
		complex(-1.0/720, 0),
		complex(0.0, 0),
		complex(1.0/40320, 0),
		complex(0.0, 0),
		complex(-1.0/3628800, 0),
		complex(0.0,0),
		complex(1.0/479001600, 0),
	}

	poly := ckks.NewPoly(coeffs)
	
	if ctOut, err = eval.EvaluatePoly(ctIn, poly, ctIn.Scale); err != nil {
		panic(err)
	}
	
	return ctOut
}

// Computing the [4/4] Pade approximant of the cosine
// This uses significantly fewer computations to reach a
// similar accuracy of the order-8 Taylor expansion of the cosine

// This turns out to be much less efficient than Taylor for some reason!
//func padeCosine(eval ckks.Evaluator, ctIn *ckks.Ciphertext) (ctOut *ckks.Ciphertext) {
//	
//	// Compute the monomials seperately
//	ct4 := eval.PowerNew(ctIn,4)
//	ct2 := eval.PowerNew(ctIn,2)
//	
//	// Multiply by coefficients and  sum
//	ctNom := eval.AddNew(eval.MultByConstNew(ct4,313.0/15120),eval.MultByConstNew(ct2,115.0/252))
//	ctNom = eval.AddConstNew(ctNom,1)
//	
//	ctDen := eval.AddNew(eval.MultByConstNew(ct4,13.0/15120),eval.MultByConstNew(ct2,11.0/252))
//	ctDen = eval.AddConstNew(ctNom,1)
//	
//	// Take the reciprocal of the denominator and then multiply
//	ctDen = eval.InverseNew(ctDen,2)
//	
//	return eval.MulNew(ctNom,ctDen)
//}

// Find the haversine of the angle between two spherical coordinates using the Haversine Formula
//func haversine(eval ckks.Evaluator, ctLat *ckks.Ciphertext, ctLon *ckks.Ciphertext, newLat float64, newLon float64) (ctOut *ckks.Ciphertext) {

//	deltaLat := eval.AddConstNew(ctLat, -newLat)
//	deltaLon := eval.AddConstNew(ctLon, -newLon)
//
//	havLat := cosine(eval,deltaLat)
//	havLat = applyLine(eval,havLat,-0.5,0.5)
	
	//return havLat

//	havLon := cosine(eval,deltaLon)
//	havLon = applyLine(eval,havLon,-0.5,0.5)

//	prodLat := eval.MultByConstNew(cosine(eval,ctLat),math.Cos(newLat))

//	havLon = eval.MulNew(prodLat,havLon)

//	hav := eval.AddNew(havLat,havLon)
	
//	return hav
//}

// Good method borrowed from Algorithm 2 Sqrt(x;d) (0<x<1), from:
// Cheon et al. 2020 Numerical Method for Comparison on Homomorphically Encrypted Numbers
// Note that error bound is (1-x/4)^(2^(d+1)) - closer to 1, the better.
func sqrt(eval ckks.Evaluator, x *ckks.Ciphertext, d int) (a *ckks.Ciphertext) {
	a = x
	b := eval.AddConstNew(x,-1)
	for n:=0;n<d;n++ {
		a = eval.MulNew(a,applyLine(eval,b,-0.5,1))
		b = eval.MulNew(eval.PowerNew(b,2),eval.MultByConstNew(applyLine(eval,b,1,-3),4))
	}
	return a
}

// Small angle approximation distance
func smallAngleDist(eval ckks.Evaluator, ctLat *ckks.Ciphertext, ctLon *ckks.Ciphertext, newLat float64, newLon float64) (ctOut *ckks.Ciphertext) {
	// Find difference in angle
	deltaLat := eval.AddConstNew(ctLat, -newLat)
	deltaLon := eval.AddConstNew(ctLon, -newLon)
	//Square both
	deltaLat = eval.PowerNew(deltaLat, 2)
	deltaLon = eval.PowerNew(deltaLon, 2)
	//Add together
	dist := eval.AddNew(deltaLat, deltaLon)
	//Take squareroot
	return dist //sqrt(eval,dist,1)
}

// Apply a linear function to data
func applyLine(eval ckks.Evaluator, ctIn *ckks.Ciphertext, grad float64, yint float64) (ctOut *ckks.Ciphertext) {
	ctOut = eval.AddConstNew(eval.MultByConstNew(ctIn,grad),yint)
	return
}

func quickText(params ckks.Parameters, val float64, encoder ckks.Encoder, encryptor ckks.Encryptor) (ctOut *ckks.Ciphertext) {
	
	values := make([]complex128, params.Slots())
	for i := range values {
		values[i] = complex(val, 0)
	}
	
	plaintext := encoder.EncodeNew(values, params.LogSlots())
	ctOut = encryptor.EncryptNew(plaintext)
	
	return 
}

func cmplx2Real(in []complex128) (out []float64) {

	out = make([]float64, len(in))
	for i, v := range in {
		out[i] = real(v)
	}
	return out
}

func handleErr(err error) {
	if err != nil {
		panic(err)
	}
}

func main() {

	 var start time.Time

	 
	 var encryptor,decryptor,encoder,evaluator,params = initializeScheme()

	 var lat1, lon1 = 0.01,0.0
	 var lat2, lon2 = 0.0,0.0
	 
	 // Fun new seed every time!
	 rand.Seed(time.Now().UTC().UnixNano())
	 
	 // Encrypt the latitude
	 cipherLat := quickText(params, lat1, encoder, encryptor)
	 
	 // Encrypt the longitude
	 cipherLon := quickText(params, lon1, encoder, encryptor)
	 
	 // Compute haversine of angle between two spherical coordinates
	 cipherDist := smallAngleDist(evaluator,cipherLat,cipherLon,lat2,lon2)
	 
	 // Obfuscate the results by displacing them over a random line
	 //cipherDist = applyLine(evaluator,cipherDist,rand.ExpFloat64()*10.0,rand.ExpFloat64()*1000.0)
	 //cipherDist = evaluator.MultByConstNew(cipherDist)
	 
	 // Decrypt the results
	 output := encoder.Decode(decryptor.DecryptNew(cipherDist), params.LogSlots())
	 real_out := cmplx2Real(output)
	 
	 // Compute some stats
	 mean, err := stats.Mean(real_out)
	 handleErr(err)
	 stdd, err := stats.StandardDeviation(real_out)
	 handleErr(err)
	 
	 // Did it work?
	 fmt.Printf("Mean:\t\t %6.10f \nStdDev:\t\t %6.10f \n",mean,stdd)
	 fmt.Println()
	 fmt.Printf("Runtime:\t %s \n", time.Since(start))
}
