function H = quarticBasis(X)

n_observations = size(X, 1);

H = [ones(n_observations, 1), X, X.^2, X.^3, X.^4];