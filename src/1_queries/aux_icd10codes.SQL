DROP TABLE IF EXISTS `mimic-iv-plus.derived.aux_icd10codes`;
CREATE TABLE `mimic-iv-plus.derived.aux_icd10codes` AS

SELECT 
    subject_id
    , hadm_id
    , CASE
       WHEN icd_version = 9 THEN icd_conv
       ELSE icd_code
      END AS icd_codes
  
  FROM `physionet-data.mimiciv_hosp.diagnoses_icd`
  AS dx
  LEFT JOIN(
    SELECT icd9, icd10 AS icd_conv
    FROM `mimic-iv-plus.derived.icd9_to_10`
  )
  AS conv
  ON conv.icd9 = dx.icd_code