.PHONY: all help cortical subcortical simulations plot_empirical plot_subcortical plot_simulations supp_empirical supp_simulations

PYTHON ?= python

all: cortical subcortical simulations plot_cortical plot_subcortical plot_simulations supp_cortical supp_simulations

help:
		@echo "Please use 'make <target>' where <target> is one of:"
		@echo "  cortical            to run all cortical (empirical) analyses"
		@echo "  subcortical         to run all subcortical (empirical) analyses"
		@echo "  simulations         to run all simulation analyses"
		@echo "  plot_cortical       to generate figures for cortical analyses"
		@echo "  plot_subcortical    to generate figures for subcortical analyses"
		@echo "  plot_simulations    to generate figures for simulation analyses"
		@echo "  supp_cortical       to run all supplementary analyses + figure-generating code"
		@echo "  supp_simulations    to run all supplementary analyses + figure-generating code"
		@echo "  all                 to run *all the things*"

cortical:
		@echo "Fetching required data\n"
		${PYTHON} scripts/cortical/fetch_data.py
		@echo "Generating eigenstrapping surrogates for HCP data\n"
		${PYTHON} scripts/cortical/generate_hcp_surrogates.py
		@echo "Running code to analyze HCP data\n"
		${PYTHON} scripts/cortical/run_hcp_nulls.py
		@echo "Generating all surrogates for Allen Human Brain Atlas and other maps\n"
		${PYTHON} scripts/cortical/generate_brainmap_surrogates.py
		@echo "Running code to analyze source-target correlations use-case\n"
		${PYTHON} scripts/cortical/run_all_correlations.py

subcortical:
		@echo "Fetching required data\n"
		${PYTHON} scripts/subcortical/fetch_data.py
		@echo "Generating surrogates for subcortical data\n"
		${PYTHON} scripts/subcortical/generate_subcortical_surrogates.py
		@echo "Running code to analyze subcortical data"
		${PYTHON} scripts/subcortical/run_subcortical_nulls.py

simulations:
		@echo "Generating simulations\n"
		${PYTHON} scripts/cortical/fetch_data.py
		${PYTHON} scripts/simulations/generate_simulations.py
		@echo "Generating ALL simulated surrogates NOTE: will take a while\n"
		${PYTHON} scripts/simulations/generate_surrogates_parallel.py
		@echo "Running correlated simulations\n"
		${PYTHON} scripts/simulations/run_simulated_nulls_parallel.py
		@echo "Running randomized simulations\n"
		${PYTHON} scripts/simulations/run_simulated_nulls_parallel.py --shuffle
		@echo "Generating Moran's I estimates\n"
		${PYTHON} scripts/simulations/run_simulated_nulls_parallel.py --run_moran
		@echo "Generating textures and surrogates\n"
		${PYTHON} scripts/simulations/generate_texture.py
		${PYTHON} scripts/simulations/generate_surrogates_parallel.py --texture
		${PYTHON} scripts/simulations/run_simulated_nulls_parallel.py --texture
		@echo "Combining simulation outputs\n"
		${PYTHON} scripts/simulations/combine_outputs.py

plot_cortical:
		@echo "Running scripts to visualize cortical (empirical) results\n"
		${PYTHON} scripts/plot_cortical/viz_hcp_nulls.py
		${PYTHON} scripts/plot_cortical/viz_use_case_nulls.py

plot_subcortical:
		@echo "Running scripts to visualize subcortical (empirical) results\n"
		${PYTHON} scripts/plot_subcortical/viz_subcortical_nulls.py

plot_simulations:
		@echo "Running scripts to visualize simulation results\n"
		${PYTHON} scripts/plot_simulations/viz_simulated_nulls.py

supp_cortical:
		@echo "Fetching required data\n"
		${PYTHON} scripts/cortical/fetch_data.py
		@echo "Running supplementary cortical analyses + generating supp figures\n"
		${PYTHON} scripts/supp_cortical/compute_residuals_amplitude_adjustment.py
		${PYTHON} scripts/supp_cortical/compute_comp_time.py
		${PYTHON} scripts/supp_cortical/compare_brainsmash_eigenstrapping.py

supp_simulations:
		@echo "Fetching required data\n"
		${PYTHON} scripts/cortical/fetch_data.py
		@echo "Running supplementary simulation analyses + generating supp figures\n"
		${PYTHON} scripts/simulations/run_simulated_nulls_parallel.py --run_moran
		${PYTHON} scripts/supp_simulations/plot_moran.py