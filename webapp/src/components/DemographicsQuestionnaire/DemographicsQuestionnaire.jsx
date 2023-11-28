import React, { useState, useEffect } from "react";
import Countries from "./countries.json";
import { SelectionField } from "./SelectionField.jsx";

export function DemographicsQuestionnaire({
  gender,
  setGender,
  age,
  setAge,
  occupation,
  setOccupation,
  education,
  setEducation,
  birthCountry,
  setBirthCountry,
  youthCountry,
  setYouthCountry,
  currentCountry,
  setCurrentCountry,
  ethnicity,
  setEthnicity,
  religion,
  setReligion,
  politicalAffiliation,
  setPoliticalAffiliation,
  englishFluency,
  setEnglishFluency,
  sexismFaced,
  setSexismFaced,
  handleSubmit,
  handleBack,
}) {
  // some constants for the questionnaire
  const occupation_options = [
    "Employed",
    "Unemployed",
    "Student",
    "Retired",
    "Homemaker",
    "Self-employed",
    "Other",
  ];
  const education_options = [
    "Less than a high school diploma",
    "High school diploma or equivalent",
    "College degree",
    "Graduate degree",
    "Other",
  ];
  const ethnic_group_options = [
    "White",
    "Black or African American",
    "Hispanic or Latino",
    "American India or Alaska Native",
    "Asian",
    "Native Hawaiian or Pacific Islander",
    "Prefer not to disclose",
  ];
  const religion_options = [
    "None",
    "Christianity",
    "Islam",
    "Hinduism",
    "Buddhism",
    "Sikhism",
    "Judaism",
    "Prefer not to disclose",
  ];
  const political_options = [
    "Left",
    "Center-Left",
    "Center",
    "Center-Right",
    "Right",
    "Prefer not to disclose",
  ];
  const english_option = [
    "1 - Very Poor",
    "2 - Poor",
    "3 - Fair",
    "4 - Good",
    "5 - Excellent",
  ];
  const age_brackets = [
    "<18",
    "18-24",
    "25-29",
    "30-34",
    "35-39",
    "40-44",
    "45-49",
    "50-54",
    "54-59",
    "60-64",
    ">65",
  ];
  const country_names = Countries.Countries.map((country) => country.name);
  const same_as_now_country = "same as now";

  const [youthCountrySelection, setYouthCountrySelection] =
    useState(same_as_now_country);
  const [birthCountrySelection, setBirthCountrySelection] =
    useState(same_as_now_country);

  const [demographicsComplete, setDemographicsComplete] = useState(false);

  // when country directly set the country for the same_as_now_option
  function handleSetBirthCountry(country) {
    setBirthCountrySelection(country);
    if (country === same_as_now_country) {
      setBirthCountry(currentCountry);
    } else {
      setBirthCountry(country);
    }
  }
  function handleSetYouthCountry(country) {
    setYouthCountrySelection(country);
    if (country === same_as_now_country) {
      setYouthCountry(currentCountry);
    } else {
      setYouthCountry(country);
    }
  }
  function handleSetCurrentCountry(country) {
    setCurrentCountry(country);
    if (birthCountrySelection === same_as_now_country) {
      setBirthCountry(country);
    }
    if (youthCountrySelection === same_as_now_country) {
      setYouthCountry(country);
    }
  }

  function canSubmitDemographics() {
    if (age < 0) return false;
    return ![
      gender,
      occupation,
      education,
      birthCountry,
      youthCountry,
      currentCountry,
      ethnicity,
      religion,
      politicalAffiliation,
      englishFluency,
      sexismFaced,
    ].includes("");
  }
  // effect to automatically update demographics completed flag
  useEffect(() => {
    setDemographicsComplete(canSubmitDemographics());
  }, [
    age,
    gender,
    occupation,
    education,
    birthCountry,
    youthCountry,
    currentCountry,
    ethnicity,
    religion,
    politicalAffiliation,
    englishFluency,
    sexismFaced,
  ]);

  function handleSubmitButton() {
    if (demographicsComplete) {
      handleSubmit();
    }
  }

  return (
    <div className="flex justify-center">
      <div className="w-1/2 bg-cyan-50 rounded-2xl p-4 mt-2 mb-2">
        <h2 className="text-black mb-2 font-bold text-xl">
          Please give us some information about yourself
        </h2>

        <SelectionField
          label="What is your gender?"
          placeholder="Gender"
          options={["Woman", "Man", "Non-binary", "Prefer not to disclose"]}
          customInputOption={"Prefer to self-describe"}
          userInput={gender}
          setUserInput={setGender}
        />

        <SelectionField
          label="What is your current age?"
          options={age_brackets}
          userInput={age}
          setUserInput={setAge}
        />

        <SelectionField
          label="What is your occupation?"
          options={occupation_options}
          userInput={occupation}
          setUserInput={setOccupation}
        />

        <SelectionField
          label="What is your education level?"
          options={education_options}
          userInput={education}
          setUserInput={setEducation}
        />

        <SelectionField
          label="Which country are you currently living in?"
          options={country_names}
          userInput={currentCountry}
          setUserInput={handleSetCurrentCountry}
        />

        <SelectionField
          label="What is your country of birth?"
          options={country_names}
          initialSelection={same_as_now_country}
          userInput={birthCountrySelection}
          setUserInput={handleSetBirthCountry}
        />

        <SelectionField
          label="In which country did you spend most of your time before you turned 18?"
          options={country_names}
          initialSelection={same_as_now_country}
          userInput={youthCountrySelection}
          setUserInput={handleSetYouthCountry}
        />

        <SelectionField
          label="What ethnic group do you belong to?"
          options={ethnic_group_options}
          customInputOption={"Prefer to self-describe"}
          userInput={ethnicity}
          setUserInput={setEthnicity}
        />

        <SelectionField
          label="What is your present religion?"
          options={religion_options}
          customInputOption={"Other"}
          userInput={religion}
          setUserInput={setReligion}
        />
        <SelectionField
          label="Which political affiliation do you most closely identify with?"
          options={political_options}
          userInput={politicalAffiliation}
          setUserInput={setPoliticalAffiliation}
        />
        <SelectionField
          label="What is your english fluency rating?"
          options={english_option}
          userInput={englishFluency}
          setUserInput={setEnglishFluency}
        />
        <SelectionField
          label="How often have you faced sexism?"
          options={["Never", "Occasionally", "Often", "Very Often"]}
          userInput={sexismFaced}
          setUserInput={setSexismFaced}
        />

        <div className="flex justify-center">
          <button
            className="py-2 px-4 rounded-full mr-2  bg-cyan-800 font-san font-bold hover:bg-cyan-500 text-white"
            onClick={handleBack}
          >
            Back
          </button>
          <button
            className={`py-2 px-4 rounded-full mr-2 ${
              demographicsComplete
                ? "bg-cyan-800 font-san font-bold hover:bg-cyan-500 text-white"
                : "bg-gray-400 font-san font-bold text-gray-700 cursor-not-allowed"
            }`}
            onClick={handleSubmitButton}
            disabled={!demographicsComplete}
          >
            Submit and start with Task!
          </button>
        </div>
      </div>
    </div>
  );
}
