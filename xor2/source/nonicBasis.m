function H = nonicBasis(X)

n_observations = size(X, 1);

H = [ones(n_observations, 1), X, X.^2, X.^3, X.^4, X.^5, X.^6, X.^7, X.^8, X.^9];