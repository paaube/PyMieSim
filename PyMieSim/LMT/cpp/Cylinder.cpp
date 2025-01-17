#include <iostream>
#include <iostream>
#include <math.h>


#pragma GCC visibility push(hidden)
class CYLINDER: public BASE{

private:
  bool       Polarized;

  double     Diameter,
             Index,
             nMedium,
             SizeParam,
             Polarization,
             Wavelength,
             k,
             E0,
             Mu,
             MuScat;

    void     ComputeAnBn(complex128* an, complex128* bn, uint MaxOrder),
             LowFreqAnBn(complex128* an, complex128* bn),
             HighFreqAnBn(complex128* an, complex128* bn, uint MaxOrder);


    public:
        Cndarray                           An(uint MaxOrder),
                                           Bn(uint MaxOrder),
                                           Cn(uint MaxOrder),
                                           Dn(uint MaxOrder);

        std::tuple<Cndarray,Cndarray>      S1S2(ndarray Phi),
                                           sS1S2(ndarray& Phi, ndarray& Theta),
                                           uS1S2(ndarray& Phi, ndarray& Theta),
                                           sFields(ndarray& Phi, ndarray& Theta, double R),
                                           uFields(ndarray& Phi, ndarray& Theta, double R);



  CYLINDER(double Index,
           double Diameter,
           double Wavelength,
           double nMedium,
           double Polarization,
           double E0)
        {
          this->Diameter      = Diameter;
          this->Index         = Index;
          this->nMedium       = nMedium;
          this->Wavelength    = Wavelength;
          this->E0            = E0;
          this->k             = 2 * PI / Wavelength;
          this->Polarization  = Polarization;
          this->SizeParam     = GetSizeParameter(Diameter, Wavelength, nMedium);
          this->Mu            = 1.0;
          this->MuScat        = 1.0;
        }

        ~CYLINDER(){  }

};

void
CYLINDER::ComputeAnBn(complex128* anPtr, complex128* bnPtr, uint MaxOrder)
{
  return HighFreqAnBn(anPtr, bnPtr, MaxOrder) ;
}


void
CYLINDER::HighFreqAnBn(complex128* anPtr, complex128* bnPtr, uint MaxOrder)
{

  double x = SizeParam;

  complex128 numerator, denominator;

  for (int order = 1; order < (int)MaxOrder+1; order++)
  {
      numerator   = Index * F90Jn(order, Index*x) * F90Jn_p(order, nMedium*x) - nMedium * F90Jn_p(order, Index*x) * F90Jn(order, nMedium*x);
      denominator = Index * F90Jn(order, Index*x) * F90H1_p(order, nMedium*x) - nMedium * F90Jn_p(order, Index*x) * F90H1(order, nMedium*x);
      anPtr[order-1] = numerator/denominator;

      numerator   = nMedium * F90Jn(order, Index*x) * F90Jn_p(order, nMedium*x) - Index*F90Jn_p(order, Index*x) * F90Jn(order, nMedium*x);
      denominator = nMedium * F90Jn(order, Index*x) * F90H1_p(order, nMedium*x) - Index*F90Jn_p(order, Index*x) * F90H1(order, nMedium*x);
      bnPtr[order-1] = numerator/denominator;
  }
}


void
CYLINDER::LowFreqAnBn(complex128* anPtr, complex128* bnPtr)
{
  double LL, m2, x3, x4, x5, x6;

  m2          = Index * Index;
  LL          = (m2 - 1) / (m2 + 2);
  x3          = SizeParam * SizeParam * SizeParam;
  x4          = x3 * SizeParam;
  x5          = x4 * SizeParam;
  x6          = x5 * SizeParam;

  anPtr[0] = (-2.*JJ * x3 / 3.) * LL - (2.*JJ * x5 / 5.) * LL * (m2 - 2.) / (m2 + 2.) + (4. * x6 / 9.) * LL * LL;
  anPtr[1] = (-1.*JJ * x5 / 15.) * (m2 - 1.) / (2. * m2 + 3.);
  bnPtr[0] = (-1.*JJ * x5 / 45.) * (m2 - 1.);
  bnPtr[1] = 0. + 0.*JJ;
}


Cndarray
CYLINDER::Bn(uint MaxOrder)
{
  Cndarray     an         = Cndarray(MaxOrder),
               bn         = Cndarray(MaxOrder);

  complex128 * anPtr      = (complex128 *) an.request().ptr,
             * bnPtr      = (complex128 *) bn.request().ptr;

  this->HighFreqAnBn(anPtr, bnPtr, MaxOrder);
  return bn;
}


Cndarray
CYLINDER::An(uint MaxOrder)
{
  Cndarray     an         = Cndarray(MaxOrder),
               bn         = Cndarray(MaxOrder);

  complex128 * anPtr      = (complex128 *) an.request().ptr,
             * bnPtr      = (complex128 *) bn.request().ptr;

  this->HighFreqAnBn(anPtr, bnPtr, MaxOrder);
  return an;
}







// -
