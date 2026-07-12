# water-net.mod   OOR2-AN-x-x
# AMPL coding: Sven Leyffer, University of Dundee, April 2000.
#
# This version expresses the integer restrictions as complementarity
# i.e. the MINLP part,
#
#      var z{arcs} >= 0, <= 1, binary;
#
#      qpup{(i,j) in arcs}: qp[i,j] <= maxq * z[i,j];
#      qnup{(i,j) in arcs}: qn[i,j] <= maxq * (1 - z[i,j]);
#
# is modelled as complementarity betwen qn[i,j] and qp[i,j], the negative
# or positive flows/pressures in each arc. Thus discard z[i,j] and write
#
#      0 <= qp[i,j] complements qn[i,j] >= 0
#
# Here model complementarity with a nonlinear equation sum qn[i,j]*qp[i,j] <= 0
#
# From an original MINLP GAMS model.
#
# THIS EXAMPLE ILLUSTRATES THE USE OF NONLINEAR PROGRAMMING IN THE DESIGN OF
# WATER DISTRIBUTION SYSTEMS. THE MODEL CAPTURES THE MAIN FEATURES OF AN
# ACTUAL APPLICATION FOR A CITY IN INDONESIA.
#
# REFERENCES: BROOKE A, DRUD A AND MEERAUS A, MODELING SYSTEMS AND
#             NONLINEAR PROGRAMMING IN A RESEARCH ENVIRONMENT,
#             IN R RAGAVAN AND S M ROHDE (EDS), COMPUTERS IN
#             ENGINEERING 1985, 1985.
#
#             DRUD D AND ROSENBORG A, DIMENSIONING WATER DISTRIBUTION
#                  NETWORKS, M. SC. DISSERTATION, (IN DANISH), INSTITUTE OF
#                  MATHEMATICAL STATISTICS AND OPERATIONS RESEARCH, TECHNICAL
#                  UNIVERSITY OF DENMARK, 1973.
#
# Number of variables:   
# Number of constraints: 
# Objective nonlinear
# Nonlinear constraints

set nodes;					# nodes
set reservoirs within nodes;
set consumers within nodes;
set arcs within nodes cross nodes;		# arcs or connections

# ... node data
param demand{nodes};				# ... demand [m^3/sec]
param height{nodes};				# ... height over base [m]
param x{nodes};					# ... x-coordinate [m]
param y{nodes};					# ... y-coordinate [m]
param supply{nodes};				# ... supply [m^3/sec]
param wcost{nodes};				# ... [rp/m**3]
param pcost{nodes};				# ... [rp/m**4]
param dist{(i,j) in arcs} 			# ... distance between nodes
      := sqrt( (x[i] - x[j])^2 + (y[i] - y[j])^2 );

# ... scalar parameters
param dpow := 5.33;		# ... power on diameter in pressure loss equation
param dmin := 0.15;		# ... minimum diameter of pipe
param dmax := 2.00;		# ... maximum diameter of pipe
param hloss := 1.03E-3;		# ... constant in the pressure loss equation
param dprc := 6.90E-2; 		# ... scale factor in the investment cost equation
param cpow := 1.29;		# ... power on diameter in the cost equation      
param r := 0.10;		# ... interest rate                               
param maxq := 2.00;		# ... bound on qp and qn                          
param davg := sqrt( dmin*dmax );# ... average diameter (geometric mean)
param rr        		# ... ratio of demand to supply
      := ( sum{i in consumers} demand[i] ) / ( sum{i in reservoirs} supply[i] );
param hl{i in nodes} := height[i] + if i in consumers then (7.5 + 5*demand[i]);

# ... variables
var qp{arcs} >= 0, <= maxq;		# ... flow on each arc - positive [m^3/sec]
var qn{arcs} >= 0, <= maxq;		# ... flow on each arc - negative [m^3/sec]
var d{arcs} >= dmin, <= dmax, := davg;	# ... pipe diameters [m]
var h{i in nodes} >= hl[i], := hl[i]+5;	# ... pressure at each node [m]
var s{ i in reservoirs} 		# ... supply at reservoir nodes
    >= 0, <= supply[i], := rr*supply[i];

minimize cost: ( sum{i in reservoirs} s[i]*pcost[i]*( h[i] - height[i] )
                 + sum{i in reservoirs} s[i]*wcost[i] ) / r 
               + dprc * sum{(i,j) in arcs} ( dist[i,j] * d[i,j]^cpow )
               + sum{(i,j) in arcs} ( qp[i,j] + qn[i,j] );

subject to

   # ... flow conservation equation at each node
   cont{i in nodes}:  sum{(j,i) in arcs} (qp[j,i] - qn[j,i]) 
                    - sum{(i,j) in arcs} (qp[i,j] - qn[i,j]) 
                    + (if i in reservoirs then s[i]) = demand[i];

   # ... pressure loss on each arc (assumes qpow = 2)
   loss{(i,j) in arcs}: (h[i] - h[j])
                        = (hloss) * dist[i,j] * (qp[i,j]^2 - qn[i,j]^2) / (d[i,j]^dpow);

   # ... complementarity
   compl: sum{(i,j) in arcs}( qp[i,j] * qn[i,j] ) <= 0;



