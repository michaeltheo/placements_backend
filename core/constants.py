from models import DikaiologitikaType, SubmissionTime, InternshipProgram

# Define the mapping
INTERNSHIP_PROGRAM_REQUIREMENTS = {
    InternshipProgram.OAED: [
        {"type": DikaiologitikaType.BebaiosiPraktikis.value,
         "description": DikaiologitikaType.get_description(DikaiologitikaType.BebaiosiPraktikis),
         "submission_time": SubmissionTime.START.value},
        {"type": DikaiologitikaType.AitisiForeaGiaApasxolisiFoititi.value,
         "description": DikaiologitikaType.get_description(DikaiologitikaType.AitisiForeaGiaApasxolisiFoititi),
         "submission_time": SubmissionTime.END.value},
    ],
    InternshipProgram.ESPA: [
        {"type": DikaiologitikaType.BebaiosiPraktikis.value,
         "description": DikaiologitikaType.get_description(DikaiologitikaType.BebaiosiApasxolisis),
         "submission_time": SubmissionTime.START.value},
        {"type": DikaiologitikaType.AsfalisiAskoumenou.value,
         "description": DikaiologitikaType.get_description(DikaiologitikaType.AsfalisiAskoumenou),
         "submission_time": SubmissionTime.END.value},
    ],
    InternshipProgram.EMPLOYER_FINANCED: [
        {"type": DikaiologitikaType.BebaiosiPraktikis.value,
         "description": DikaiologitikaType.get_description(DikaiologitikaType.BebaiosiPraktikis),
         "submission_time": SubmissionTime.START.value},
        {"type": DikaiologitikaType.BebaiosiPraktikis.value,
         "description": DikaiologitikaType.get_description(DikaiologitikaType.BebaiosiPraktikis),
         "submission_time": SubmissionTime.END.value},
    ],
}
