source("src/models/utils.R")

treatments <- read.delim("config/treatments.txt")
confounders <- read.delim("config/confounders.txt")

days <- c(1, 2, 3, 4)
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

for (day in days) {

    print(paste0("Day: ", day))

    for (j in 1:nrow(treatments)) {

        data <- read.csv(paste0("data/clean/coh_4/day_", day, "_", trts[j],".csv"))

        model_confounders <- read_confounders(j, treatments, confounders) 
        treatment <- treatments$treatment[j]

        print(paste0("Treatment: ", treatment))

        # create formula to input to a glm
        formula <- paste(treatment, "~", paste(model_confounders, collapse = " + "))

        # create a glm
        model <- glm(formula, data = data, family = binomial(link = "logit"))

        # odds ratios, CI
        df <- as.data.frame(exp(cbind(OR = coef(model), confint(model))), N = nrow(data))

        results_df[nrow(results_df) + 1,] <- c(day,
                                               treatment,
                                               df["race_white", 1],
                                               df["race_white", 2],
                                               df["race_white", 3]
                                               ) 
        write.csv(results_df, "results/models/log_reg_1_coh.csv", row.names = FALSE)
    }
}




