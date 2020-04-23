## greet
* greet
  - utter_greet
  - utter_menu

## menu
* menu
  - utter_menu

## about_corona
* about_corona
  - utter_about_corona
  
## covid_test
* covid_test
  - utter_covid_test

## symptoms
* symptoms
  - utter_symptoms

## precaution
* precaution
  - utter_precaution
  
## my_area_cases
* my_area_cases
  - utter_my_area_cases
  - utter_enter_name
* enter_name{"name": "vishweswar"}
  - action_set_name
  - utter_enter_email
* enter_email{"email": "vishweswar53@gmail.com"}
  - action_set_email
  - utter_enter_mobile
* enter_mobile{"mobile": "7894561230"}
  - action_set_mobile
  - utter_enter_pincode
* enter_pincode{"pincode": "390013"}
  - action_set_pincode
  - user_details_form
  - form{"name": "user_details_form"}
  - form{"name": null}

## news
* news
  - utter_news
  - action_news

## india_cases
* india_cases
  - utter_india_cases
  - action_india_cases

## state_cases
* state_cases
  - utter_state_cases
  - utter_enter_state
* enter_state
  - action_set_state
  - state_form
  - form{"name": "state_form"}
  - form{"name": null}

## global_cases
* global_cases
  - utter_global_cases
  - action_global_cases

## country_cases
* country_cases
  - utter_country_cases
  - utter_enter_country
* enter_country
  - action_set_country
  - country_form
  - form{"name": "country_form"}
  - form{"name": null}

## covid_map
* covid_map
  - utter_covid_map

## quarantine_tips
* quarantine_tips
  - utter_quarantine_tips1
  - utter_quarantine_tips2
  - utter_quarantine_tips3

## myth_buster
* myth_buster
  - utter_myth_buster1
  - utter_myth_buster2
  - utter_myth_buster3
  - utter_myth_buster4
  - utter_myth_buster5
  - utter_myth_buster6
  - utter_myth_buster7

## goodbye
* goodbye
  - utter_goodbye
