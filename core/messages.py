class Messages:
    COMPANY_ALREADY_SUBMITTED_ANSWERS = "Η εταιρεία έχει ήδη υποβάλλει το ερωτηματολόγιο για αυτήν την πρακτική."
    QUESTION_NOT_FOUND = "Η ερώτηση με ID: {question_id} δεν βρέθηκε."
    NOT_A_COMPANY_QUESTION = "Η ερώτηση με ID: {question_id} δεν ανήκει στο ερωτηματολόγιο της εταιρείας."
    NOT_A_STUDENT_QUESTION = "Η ερώτηση με ID: {question_id} δεν ανήκει στο ερωτηματολόγιο του φοιτητή."
    FOUND_DOUBLE_ANSWER = "Βρέθηκαν διπλές απαντήσεις για την ερώτηση με ID: {question_id}."
    INVALID_ANSWER_OPTION_IDS = "Μη έγκυρη ID απάντησης: {invalid_option_ids} για την ερώτηση με ID: {question_id}."
    MULTIPLE_ANSWERS_NOT_SUPPORTED = "Αυτή η ερώτηση δεν υποστηρίζει πολλαπλές απαντήσεις."
    INTERNSHIP_NOT_FOUND = 'Η πρακτική άσκηση δεν βρέθηκε.'
    COMPANY_NOT_FOUND = 'Η εταιρεία δεν βρέθηκε.'
    MULTIPLE_ANSWERS_CHECK = 'Για τις ερωτήσεις πολλαπλής επιλογής απαιτείται μία απο τις επιλογές απάντησης.'
    FREE_TEXT_ANSWER_OPTION_CHECK = 'Η ερώτησης τύπου free-text, δεν πρέπει να έχουν επιλογές απάντησεις'
    INVALID_STATE = "Μη έγκυρη παράμετρος state."
    INVALID_TOKEN = "Μη έγκυρο token."
    SUCCESSFULLY_LOGIN = "Είσοδος χρήστη με επιτυχία."
    TOKEN_VALIDATION_ERROR = "Παρουσιάστηκε σφάλμα, δοκιμάστε να συνδεθείτε ξανά."
    FETCH_TOKEN_ERROR = "Αποτυχία λήψης token."
    FETCH_PROFILE_ERROR = 'Αποτυχία λήψης προφίλ.'
    USER_NOT_FOUND = 'Ο χρήστης δεν βρέθηκε.'
    UNAUTHORIZED_USER = "Ο χρήστης δεν είναι εξουσιοδοτημένος να εκτελέσει αυτήν την ενέργεια."
    COMPANY_DELETION_FAILED = "Η εταιρεία δεν βρέθηκε ή δεν ήταν δυνατή η διαγραφή της."
    ALL_COMPANIES_RETRIEVED = "Όλες οι εταιρείες ανακτήθηκαν με επιτυχία."
    COMPANY_ALREADY_EXISTS = "Μια εταιρεία με αυτό το ΑΦΜ υπάρχει ήδη."
    COMPANY_CREATED_SUCCESS = "Η εταιρεία {company_name} δημιουργήθηκε με επιτυχία."
    COMPANY_UPDATED_SUCCESS = "Η εταιρεία {company_name} ενημερώθηκε με επιτυχία."
    COMPANY_DELETED_SUCCESS = "Η εταιρεία διαγράφηκε με επιτυχία."
    COMPANY_ANSWERS_INVALID_TOKEN = "Μη έγκυρο ή ληγμένο token. Παρακαλώ εισάγετε νέο κωδικό OTP."
    COMPANY_ANSWERS_SUCCESSFULLY_SUBMIT = 'Οι απαντήσεις της εταιρείας υποβλήθηκαν με επιτυχία.'
    COMPANY_ANSWERS_RETRIEVED = 'Οι απαντήσεις της εταιρείας ανακτήθηκαν με επιτυχία.'
    COMPANY_ANSWERS_DELETED_SUCCESS = 'Όλες οι απαντήσεις της εταιρείας έχουν διαγραφεί.'
    COMPANY_ANSWERS_DELETION_FAILED = 'Δεν βρέθηκαν απαντήσεις για διαγραφή ή δεν ήταν δυνατή η διαγραφή.'
    FILE_NOT_FOUND = "Το αρχείο δεν βρέθηκε."
    FILE_UPLOADED_SUCCESS = "Το αρχείο ανέβηκε με επιτυχία."
    FILE_UPDATED_SUCCESS = "Το αρχείο ενημερώθηκε με επιτυχία."
    FILE_DELETED_SUCCESS = "Το αρχείο διαγράφηκε με επιτυχία."
    FILE_ACCESS_FORBIDDEN = "Δεν έχετε άδεια πρόσβασης σε αυτά τα αρχεία."
    FILE_DOWNLOAD_FORBIDDEN = "Δεν έχετε άδεια να κατεβάσετε αυτό το αρχείο."
    FILE_MUST_BE_PDF = "Το αρχείο πρέπει να είναι PDF."
    FILE_ALREADY_SUBMITTED = "Έχετε ήδη υποβάλει αυτόν τον τύπο αρχείου."
    FILES_RETRIEVED_SUCCESS = "Τα αρχεία ανακτήθηκαν."
    DIKAIOLOGITIKA_TYPES_RETRIEVED_SUCCESS = ("Λίστα όλων των τύπων Δικαιολογητικών για κάθε Πρόγραμμα Πρακτικής "
                                              "Άσκησης.")
    INTERNSHIP_DELETION_FAILED = "Η πρακτική άσκηση δεν βρέθηκε ή δεν ήταν δυνατή η διαγραφή της."
    ALL_INTERNSHIPS_RETRIEVED = "Οι πρακτικές ασκήσεις ανακτήθηκαν με επιτυχία."
    INTERNSHIP_CREATED_OR_UPDATED = "Η πρακτική άσκηση δημιουργήθηκε ή ενημερώθηκε με επιτυχία."
    INTERNSHIP_RETRIEVED_FOR_USER = "Η πρακτική άσκηση ανακτήθηκε για τον χρήστη {user_name}."
    INTERNSHIP_DELETED_SUCCESS = "Η πρακτική άσκηση διαγράφηκε με επιτυχία."
    INTERNSHIP_STATUS_UPDATED = "Η πρακτική άσκηση ενημερώθηκε με επιτυχία."
    OTP_GENERATION_SUCCESS = "Ο κωδικός OTP δημιουργήθηκε με επιτυχία."
    OTP_VALIDATION_SUCCESS = "Η επικύρωση του κωδικού OTP ήταν επιτυχής!"
    INVALID_OR_EXPIRED_OTP = "Μη έγκυρος ή ληγμένος κωδικός OTP."
    COMPANY_NOT_FOUND_FOR_INTERNSHIP = "Αυτή η πρακτική άσκηση δεν έχει εταιρεία."
    OTP_GENERATION_FAILED = "Αποτυχία δημιουργίας κωδικού OTP."
    QUESTION_TYPES_RETRIEVED = "Λίστα όλων των τύπων ερωτήσεων."
    QUESTIONS_CREATED_SUCCESS = "Οι ερωτήσεις δημιουργήθηκαν με επιτυχία."
    QUESTIONS_RETRIEVED_SUCCESS = "Οι ερωτήσεις ανακτήθηκαν με επιτυχία."
    QUESTION_UPDATED_SUCCESS = "Η ερώτηση ενημερώθηκε με επιτυχία."
    QUESTION_DELETED_SUCCESS = "Η ερώτηση διαγράφηκε."
    QUESTION_STATISTICS_RETRIEVED = "Τα στατιστικά ανακτήθηκαν με επιτυχία."
    QUESTION_DELETION_FAILED = "Η ερώτηση δεν βρέθηκε ή δεν ήταν δυνατή η διαγραφή της."
    USER_ANSWERS_DELETION_FAILED = "Δεν βρέθηκαν απαντήσεις για διαγραφή ή δεν ήταν δυνατή η διαγραφή."
    ANSWERS_SUBMITTED_SUCCESS = "Οι απαντήσεις υποβλήθηκαν με επιτυχία."
    ANSWERS_RETRIEVED_SUCCESS = "Οι απαντήσεις ανακτήθηκαν με επιτυχία."
    ANSWERS_DELETED_SUCCESS = "Όλες οι απαντήσεις του χρήστη έχουν διαγραφεί."
    DEPARTMENT_TYPES_RETRIEVED = "Λίστα όλων των τύπων Τμημάτων."
    USERS_RETRIEVED_SUCCESS = "Οι χρήστες ανακτήθηκαν με επιτυχία."
    USER_PROCESSED_SUCCESS = "Ο χρήστης επεξεργάστηκε με επιτυχία."
    USER_RETRIEVED_SUCCESS = "Ο χρήστης ανακτήθηκε με επιτυχία."
    USER_PROMOTED_TO_ADMIN = "Ο χρήστης: {user_name} προήχθη σε διαχειριστή."
    USER_DEMOTED_TO_STUDENT = "Ο χρήστης: {user_name} υποβαθμίστηκε σε φοιτητή."
    USER_PROFILE_UPDATE_SUCCESSFULLY = 'Το προφίλ ενημερώθηκε με επιτυχία.'
    USER_WITH_SAME_AM_EXISTS = 'Υπάρχει ήδη χρήστης με το υπάρχων ΑΜ.'
    INVALID_ROLE = "Μη έγκυρος ρόλος."
    INVALID_DEPARTMENT = "Μη έγκυρο τμήμα."
