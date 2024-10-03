from models import DikaiologitikaType, SubmissionTime, InternshipProgram

# Define the mapping
INTERNSHIP_PROGRAM_REQUIREMENTS = {
    InternshipProgram.TEITHE_OAED: [{"type": DikaiologitikaType.AitisiPraktikis.value,
                                     "description": DikaiologitikaType.get_description(
                                         DikaiologitikaType.AitisiPraktikis),
                                     "submission_time": SubmissionTime.START.value},
                                    {"type": DikaiologitikaType.BebaiosiPraktikisApoGramateia.value,
                                     "description": DikaiologitikaType.get_description(
                                         DikaiologitikaType.BebaiosiPraktikisApoGramateia),
                                     "submission_time": SubmissionTime.START.value},
                                    {"type": DikaiologitikaType.AitisiForeaGiaApasxolisiFoititi.value,
                                     "description": DikaiologitikaType.get_description(
                                         DikaiologitikaType.AitisiForeaGiaApasxolisiFoititi),
                                     "submission_time": SubmissionTime.START.value},

                                    {"type": DikaiologitikaType.AntigraphoE3_5.value,
                                     "description": DikaiologitikaType.get_description(
                                         DikaiologitikaType.AntigraphoE3_5),
                                     "submission_time": SubmissionTime.END.value},

                                    {"type": DikaiologitikaType.BebaiosiEnsimonApoEfka.value,
                                     "description": DikaiologitikaType.get_description(
                                         DikaiologitikaType.BebaiosiEnsimonApoEfka),
                                     "submission_time": SubmissionTime.END.value},
                                    {
                                        "type": DikaiologitikaType.BebaiosiApasxolisisKaiAsfalisisAskoumenou.value,
                                        "description": DikaiologitikaType.get_description(
                                            DikaiologitikaType.BebaiosiApasxolisisKaiAsfalisisAskoumenou),
                                        "submission_time": SubmissionTime.START.value},

                                    {"type": DikaiologitikaType.ApodeixeisEjoflisisMinaiasApozimiosis.value,
                                     "description": DikaiologitikaType.get_description(
                                         DikaiologitikaType.ApodeixeisEjoflisisMinaiasApozimiosis),
                                     "submission_time": SubmissionTime.END.value},
                                    {"type": DikaiologitikaType.AitisiOlokrirosisPraktikisAskisis.value,
                                     "description": DikaiologitikaType.get_description(
                                         DikaiologitikaType.AitisiOlokrirosisPraktikisAskisis),
                                     "submission_time": SubmissionTime.END.value},
                                    {"type": DikaiologitikaType.BebaiosiOlokrilosisPraktikisAskisis.value,
                                     "description": DikaiologitikaType.get_description(
                                         DikaiologitikaType.BebaiosiOlokrilosisPraktikisAskisis),
                                     "submission_time": SubmissionTime.END.value},

                                    ],
    InternshipProgram.ESPA: [
        {"type": DikaiologitikaType.AitisiPraktikis.value,
         "description": DikaiologitikaType.get_description(DikaiologitikaType.AitisiPraktikis),
         "submission_time": SubmissionTime.START.value},
        {"type": DikaiologitikaType.BebaiosiPraktikisApoGramateia.value,
         "description": DikaiologitikaType.get_description(DikaiologitikaType.BebaiosiPraktikisApoGramateia),
         "submission_time": SubmissionTime.START.value},
        {"type": DikaiologitikaType.AitisiForeaGiaApasxolisiFoititi.value,
         "description": DikaiologitikaType.get_description(DikaiologitikaType.AitisiForeaGiaApasxolisiFoititi),
         "submission_time": SubmissionTime.START.value},
        {
            "type": DikaiologitikaType.BebaiosiApasxolisisKaiAsfalisisAskoumenou.value,
            "description": DikaiologitikaType.get_description(
                DikaiologitikaType.BebaiosiApasxolisisKaiAsfalisisAskoumenou),
            "submission_time": SubmissionTime.START.value},

        {"type": DikaiologitikaType.DilosiAtomikonStoixeion.value,
         "description": DikaiologitikaType.get_description(DikaiologitikaType.DilosiAtomikonStoixeion),
         "submission_time": SubmissionTime.START.value},
        {"type": DikaiologitikaType.YpeuthiniDilosiProsopikonDedomenon.value,
         "description": DikaiologitikaType.get_description(DikaiologitikaType.YpeuthiniDilosiProsopikonDedomenon),
         "submission_time": SubmissionTime.START.value},
        {"type": DikaiologitikaType.DilosiMoriodotisi.value,
         "description": DikaiologitikaType.get_description(DikaiologitikaType.DilosiMoriodotisi),
         "submission_time": SubmissionTime.START.value},

        {"type": DikaiologitikaType.AitisiOlokrirosisPraktikisAskisis.value,
         "description": DikaiologitikaType.get_description(DikaiologitikaType.AitisiOlokrirosisPraktikisAskisis),
         "submission_time": SubmissionTime.END.value},
        {"type": DikaiologitikaType.BebaiosiOlokrilosisPraktikisAskisis.value,
         "description": DikaiologitikaType.get_description(
             DikaiologitikaType.BebaiosiOlokrilosisPraktikisAskisis),
         "submission_time": SubmissionTime.END.value},

    ],
    InternshipProgram.TEITHE_JOB_RECOGNITION: [
        {"type": DikaiologitikaType.AitisiPraktikis.value,
         "description": DikaiologitikaType.get_description(DikaiologitikaType.AitisiPraktikis),
         "submission_time": SubmissionTime.START.value},
        {"type": DikaiologitikaType.BebaiosiPraktikisApoGramateia.value,
         "description": DikaiologitikaType.get_description(DikaiologitikaType.BebaiosiPraktikisApoGramateia),
         "submission_time": SubmissionTime.START.value},
        {
            "type": DikaiologitikaType.AnagnorisiErgasias.value,
            "description": DikaiologitikaType.get_description(DikaiologitikaType.AnagnorisiErgasias),
            "submission_time": SubmissionTime.START.value
        }, {
            "type": DikaiologitikaType.BebaiosiApasxolisisKaiAsfalisisAskoumenou.value,
            "description": DikaiologitikaType.get_description(
                DikaiologitikaType.BebaiosiApasxolisisKaiAsfalisisAskoumenou),
            "submission_time": SubmissionTime.START.value}, {
            "type": DikaiologitikaType.SimbasiErgasias.value,
            "description": DikaiologitikaType.get_description(
                DikaiologitikaType.SimbasiErgasias),
            "submission_time": SubmissionTime.START.value},
        {"type": DikaiologitikaType.AntigraphoE3_5.value,
         "description": DikaiologitikaType.get_description(
             DikaiologitikaType.AntigraphoE3_5),
         "submission_time": SubmissionTime.END.value},
        {"type": DikaiologitikaType.ApodeixeisEjoflisisMinaiasApozimiosis.value,
         "description": DikaiologitikaType.get_description(DikaiologitikaType.ApodeixeisEjoflisisMinaiasApozimiosis),
         "submission_time": SubmissionTime.END.value},
        {"type": DikaiologitikaType.BebaiosiEnsimonApoEfka.value,
         "description": DikaiologitikaType.get_description(DikaiologitikaType.BebaiosiEnsimonApoEfka),
         "submission_time": SubmissionTime.END.value},
        {"type": DikaiologitikaType.BebaiosiOlokrilosisPraktikisAskisis.value,
         "description": DikaiologitikaType.get_description(
             DikaiologitikaType.BebaiosiOlokrilosisPraktikisAskisis),
         "submission_time": SubmissionTime.END.value},
    ],
    InternshipProgram.EMPLOYER_DECLARATION_OF_RESPONSIBILITY: [
        {"type": DikaiologitikaType.AitisiPraktikis.value,
         "description": DikaiologitikaType.get_description(DikaiologitikaType.AitisiPraktikis),
         "submission_time": SubmissionTime.START.value},
        {"type": DikaiologitikaType.BebaiosiPraktikisApoGramateia.value,
         "description": DikaiologitikaType.get_description(DikaiologitikaType.BebaiosiPraktikisApoGramateia),
         "submission_time": SubmissionTime.START.value},
        {"type": DikaiologitikaType.AitisiForeaGiaApasxolisiFoititi.value,
         "description": DikaiologitikaType.get_description(DikaiologitikaType.AitisiForeaGiaApasxolisiFoititi),
         "submission_time": SubmissionTime.START.value},
        {"type": DikaiologitikaType.YpeuthiniDilosiErgodoti.value,
         "description": DikaiologitikaType.get_description(DikaiologitikaType.YpeuthiniDilosiErgodoti),
         "submission_time": SubmissionTime.START.value},
        {
            "type": DikaiologitikaType.BebaiosiApasxolisisKaiAsfalisisAskoumenou.value,
            "description": DikaiologitikaType.get_description(
                DikaiologitikaType.BebaiosiApasxolisisKaiAsfalisisAskoumenou),
            "submission_time": SubmissionTime.START.value},

        {"type": DikaiologitikaType.AntigraphoE3_5.value,
         "description": DikaiologitikaType.get_description(DikaiologitikaType.AntigraphoE3_5),
         "submission_time": SubmissionTime.END.value},

        {"type": DikaiologitikaType.BebaiosiEnsimonApoEfka.value,
         "description": DikaiologitikaType.get_description(DikaiologitikaType.BebaiosiEnsimonApoEfka),
         "submission_time": SubmissionTime.END.value},

        {"type": DikaiologitikaType.ApodeixeisEjoflisisMinaiasApozimiosis.value,
         "description": DikaiologitikaType.get_description(DikaiologitikaType.ApodeixeisEjoflisisMinaiasApozimiosis),
         "submission_time": SubmissionTime.END.value},
        {"type": DikaiologitikaType.AitisiOlokrirosisPraktikisAskisis.value,
         "description": DikaiologitikaType.get_description(DikaiologitikaType.AitisiOlokrirosisPraktikisAskisis),
         "submission_time": SubmissionTime.END.value},
        {"type": DikaiologitikaType.BebaiosiOlokrilosisPraktikisAskisis.value,
         "description": DikaiologitikaType.get_description(
             DikaiologitikaType.BebaiosiOlokrilosisPraktikisAskisis),
         "submission_time": SubmissionTime.END.value},

    ],
}
