% Rank combinations of parts based on the fit scores

function [ranked_score_new, action_part_idx, grasp_part_idx] = parts_combo(action_scores, grasp_scores, action_scale, grasp_scale, ranked_action_params, ranked_grasp_params)

ranked_score_total = [];
action_part_idx = [];
grasp_part_idx = [];

e_shape = [];
e_scale = [];
e_ratio = [];

relative_scaling = action_scale./grasp_scale;

%Adding relative scale normalization
rel_max = sum(relative_scaling);
relative_scaling = relative_scaling/rel_max;

for i = 1:length(action_scores)
    for j = 1:length(grasp_scores)
        if j ~= i
            relative_parts_scale = ranked_action_params(i,1:3)./ranked_grasp_params(j,1:3);
            
            %Adding relative scale normalization
            rel_max = sum(relative_parts_scale);
            relative_parts_scale = relative_parts_scale/rel_max;
            
            %score_total = sqrt(sum((relative_parts_scale - relative_scaling).^2)) + action_scores(i) + grasp_scores(j);
            rel_diff = abs(relative_parts_scale - relative_scaling);
            score_total = sum(rel_diff) + action_scores(i) + grasp_scores(j);
            
            e_shape = horzcat(e_shape, action_scores(i) + grasp_scores(i));
            e_ratio = horzcat(e_ratio, sum(abs(relative_parts_scale - relative_scaling)));
            e_scale = horzcat(e_scale, sum(abs(action_scale - ranked_action_params(i,1:3))) + sum(abs(grasp_scale - ranked_grasp_params(i,1:3))));
            
            score_total = score_total + 1*(sum(abs(action_scale - ranked_action_params(i,1:3))) + sum(abs(grasp_scale - ranked_grasp_params(i,1:3))));
            ranked_score_total = horzcat(ranked_score_total, score_total);
            action_part_idx = horzcat(action_part_idx, i);
            grasp_part_idx = horzcat(grasp_part_idx, j);
        end
    end
end

ranked_score_new = ranked_score_total;

e_shape = var(e_shape)
e_ratio = var(e_ratio)
e_scale = var(e_scale)

end
