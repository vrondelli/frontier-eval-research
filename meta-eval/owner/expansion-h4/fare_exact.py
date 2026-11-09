"""Owner successor exact-rational implementation of original K/V/D/T/W/R."""
import re
from fractions import Fraction
def rounded(x):
    sign=-1 if x<0 else 1;n=abs(x.numerator);q,r=divmod(n,x.denominator)
    return sign*(q+(2*r>=x.denominator))
def settle_fares(records):
    total=0;fares={};classes={};excluded=[]
    for r in records:
        p=r['passcode'];f=r['fare'];b=r['baggage'];v=r['voucher'];d=r['sailed'];ident=r['passenger']
        valid=(re.fullmatch(r'[0-9]{5}(?:-[0-9]{3})?',p)is not None and re.fullmatch(r'[0-9]+(?:\.[0-9]+)?',f)is not None and re.fullmatch(r'[0-9]+(?:\.[0-9]+)?',b)is not None and re.fullmatch(r'-?[0-9]+(?:\.[0-9]+)?',v)is not None and re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}',d)is not None)
        if valid:
            y,m,day=map(int,d.split('-'));valid=1<=m<=12 and 1<=day<=31 and (y,m,day)<=(2025,6,20) and Fraction(f)>0 and Fraction(b)>0
        if not valid:excluded.append(ident);continue
        prefix=int(p[:2]);i=0 if prefix<=18 else 1 if prefix<=49 else 2 if prefix<=73 else 3
        name=['youth','adult','resident','priority'][i];levy=[3,5,8,13][i];rate=Fraction([7,12,19,26][i],100)
        combined=Fraction(f)+Fraction(b);raw=combined-min(combined*Fraction(9,100),18)
        four=raw*4;charge=Fraction(-(-four.numerator//four.denominator),4)
        amount=(levy+rate*charge+2)*Fraction(107,100)+(6 if i==3 else 0)-Fraction(v)
        minor=rounded(amount*100);fares[ident]=minor;classes[name]=classes.get(name,0)+minor;total+=minor
    count=len(fares)
    return {'total_minor':total,'billed':count,'excluded':excluded,'fares':fares,'per_class':classes,'mean_minor':rounded(Fraction(total,count))if count else 0}
