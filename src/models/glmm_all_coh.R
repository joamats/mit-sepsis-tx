source("src/models/utils.R")

library(lme4)

treatments <- read.delim("config/treatments.txt")
confounders <- read.delim("config/confounders.txt")

cohort_numbers <- c(1, 2, 3, 4)
# create treatments list with MV, RRT, VP
trts <- c("MV", "RRT", "VP")

# Dataframe to hold results
results_df <- data.frame(matrix(ncol=5, nrow=0))
colnames(results_df) <- c(
                        "cohort",
                        "treatment",
                        "OR",
                        "2.5%",
                        "97.5%"
                        )

for (cohort_number in cohort_numbers) {

    print(paste0("Cohort: ", cohort_number))

    for (j in 1:nrow(treatments)) {

        data <- read.csv(paste0("data/clean/coh_", cohort_number, "_", trts[j],".csv"))
        # add identifier to each row
        data$patient <- 1:nrow(data)

        model_confounders <- read_confounders(j, treatments, confounders) 
        treatment <- treatments$treatment[j]

        print(paste0("Treatment: ", treatment))

        # create formula to input to a glm
        formula <- paste(treatment, "~", paste(model_confounders, collapse = " + "),
                         "+ (1 | race_white)") # change to cohort level instead of patient

        # create a glm
        model <- glmer(formula, data = data, family = binomial)

        # odds ratios, CI
        df <- as.data.frame(exp(cbind(OR = coef(model), confint(model))), N = nrow(data))

        results_df[nrow(results_df) + 1,] <- c(cohort_number,
                                               treatment,
                                               df["race_white", 1],
                                               df["race_white", 2],
                                               df["race_white", 3]
                                               ) 
        write.csv(results_df, "results/models/glmm_all_coh.csv", row.names = FALSE)
    }
}

