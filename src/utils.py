
def random_unit_vector():

  from numpy.random import multivariate_normal
  from numpy import sqrt, sum, square, reshape

  x = multivariate_normal(mean=[0]*3,cov=[[1,0,0],[0,1,0],[0,0,1]],size=1)
  l = sqrt(sum(square(x)))

  return reshape(x/l,3)

