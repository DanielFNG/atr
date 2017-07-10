function [ reference_trajectory ] = convertRefTraj( trajectory )
% Given a vector, which is an array of encoder values given by the 1D arm,
% convert these to radians and produce a new reference trajectory, which
% can then be used elsewhere i.e. in the PID code.

ENC_TICKS_PER_TURN = 220092;
ENC2RAD = 2*pi/ENC_TICKS_PER_TURN;
reference_trajectory = ENC2RAD*(trajectory(1:end) - trajectory(1));

end

