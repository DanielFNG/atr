%% Form the array of values for $k$. 
k = 0:10/99:10;

%% Form the percentage mean and std from the raw results. 
thigh_y_mean_percent = thigh_y_mean/known_max_y_thigh * 100;
thigh_y_std_percent = thigh_y_std/known_max_y_thigh * 100;

shank_y_mean_percent = shank_y_mean/known_max_y_shank * 100;
shank_y_std_percent = shank_y_std/known_max_y_shank * 100;

%% Calculate and display values for table. 
fprintf('\nShowing results for thigh.\n');
for i=[10,5,1]
    for j=[5,1]
        locs = findIndices(thigh_y_mean_percent, i, thigh_y_std_percent, j, 'column');
        loc = bestLocs(locs, thigh_y_mean_percent);
        n_iterations = loc(1,2);
        k_value = k(loc(1,1));
        fprintf('For mean %i and s.d. %i put k %f and iterations %i.\n', i, j, k_value, n_iterations + 2);
    end
end

fprintf('\nShowing results for shank.\n');
for i=[10,5,1]
    for j=[5,1]
        locs = findIndices(shank_y_mean_percent, i, shank_y_std_percent, j, 'column');
        loc = bestLocs(locs, shank_y_mean_percent);
        n_iterations = loc(1,2);
        k_value = k(loc(1,1));
        fprintf('For mean %i and s.d. %i put k %f and iterations %i.\n', i, j, k_value, n_iterations + 2);
    end
end