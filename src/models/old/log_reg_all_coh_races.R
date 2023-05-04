source("src/models/utils.R")

treatments <- read.delim("config/treatments.txt")
confounders <- read.delim("config/confounders_races.txt")

cohort_numbers <- c(1, 2, 3, 4)
# create treatments list with MV, RRT, VP
trts <- c("MV", "RRT", "VP")
races <- c("race_black", "race_hisp", "race_asian")

# Dataframe to hold results
results_df <- data.frame(matrix(ncol=6, nrow=0))
colnames(results_df) <- c(
                        "cohort",
                        "race",
                        "treatment",
                        "OR",
                        "2.5%",
                        "97.5%"
                        )

for (cohort_number in cohort_numbers) {

    print(paste0("Cohort: ", cohort_number))

    for (j in 1:nrow(treatments)) {

        data <- read.csv(paste0("data/clean/coh_", cohort_number, "_", trts[j],".csv"))

        model_confounders <- read_confounders(j, treatments, confounders) 
        treatment <- treatments$treatment[j]

        print(paste0("Treatment: ", treatment))

        # Add white as reference (0)
        results_df[nrow(results_df) + 1,] <- c(cohort_number,
                                              "race_white",
                                               treatment,
                                               1,1,1
                                    ) 

        for(r in races) {

            print(paste0("Race-Ethinicity: ", r))

            # Create data subset where race is not na
            subset <- data[!is.na(data[, r]), ]

            # Print no. of dropped rows
            print(paste0("Dropped rows: ", nrow(data) - nrow(subset)))

            # Append race to model confounders
            model_confounders_race <- c(model_confounders, r)

            # create formula to input to a glm
            formula <- paste(treatment, "~", paste(model_confounders_race, collapse = " + "))
            # create a glm
            model <- glm(formula, data = subset, family = binomial(link = "logit"))

            # odds ratios, CI
            df <- as.data.frame(exp(cbind(OR = coef(model), confint(model))), N = nrow(subset))

            results_df[nrow(results_df) + 1,] <- c(cohort_number,
                                                   r,
                                                   treatment,
                                                   df[r, 1],
                                                   df[r, 2],
                                                   df[r, 3]
                                                ) 
            write.csv(results_df, "results/models/log_reg_all_coh_races.csv", row.names = FALSE)
        }
    }
}




