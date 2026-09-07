"""Source-anchored, assistant-authored benchmark; no LLM calls or human validation.

The 60/42/18 design is a project choice. Existing 13 questions stay in their
original file as legacy regression data. References bind source passages and
quotes, then resolve all containing windows without treating sibling IDs as new
independent evidence. Test answers must never select a configuration.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from navigator.common import ROOT, digest, write_json, load_config
from navigator.corpus import prepare
from navigator.evaluation import validate_questions

S={'G':'PMC7503443','I':'PMC8039127','R':'PMC8963195'}
def F(s,p,quote,text): return (S[s],p,quote,text)
# Each row is (question, required facts, required qualifications).
# The final three rows of each slice are test-only; related reference passages
# are checked for cross-split leakage below.
rows={
'direct':[
('What were the two stated aims of the Italian center study?', [F('I',17,'to describe the genotypes and the clinical findings','Describe genotypes and clinical findings.'),F('I',17,'to highlight the changing strategy in the management of these patients over time','Describe management changes over time.')],[]),
('How many patients were included in the Italian retrospective cohort and during what period?', [F('I',19,'Data of 22 patients affected by CCHS has been collected retrospectively.','22 patients, retrospectively.'),F('I',19,'between 2000 and 2020','Follow-up period 2000–2020.')],[]),
('Which records supplied the Italian study data and what approval is reported?', [F('I',21,'review of the electronic medical record with the approval from the Institutional Review Board','Electronic medical records, with Institutional Review Board approval.')],[]),
('Which organization performed the initial literature search for the European guideline?', [F('G',12,'Centre for Reviews and Dissemination at the University of York, UK','Centre for Reviews and Dissemination, University of York.')],[]),
('What limitations do the Italian authors state about design, sample and population?', [F('I',68,'retrospective design, the poor sample, and the heterogeneity of the described population','Retrospective design, small sample and heterogeneous population.'),F('I',68,'patients of different ages and who had experienced different primary care settings','Different ages and prior care settings.')],[]),
('Which two additional genes does the guideline report in consanguineous families?', [F('G',60,'MYO1H and LBX1','MYO1H and LBX1.')],[F('G',60,'two consanguineous families with CCHS','Reported in two families; not a universal cause.')]),
('What share of the Italian cohort had PARMs versus NPARMs?', [F('I',32,'19/22 cases (86%) and NPARMs in 3/22 cases (14%)','PARMs 19/22 (86%); NPARMs 3/22 (14%).')],[]),
('At what ages were the two adult women diagnosed in the Italian cohort?', [F('I',28,'at 35 and 38 years in two adult female patients','35 and 38 years.')],[F('I',28,'after the detection of genetic mutation in their children','Diagnosis followed detection in their children.')]),
('In what year does the guideline say PHOX2B was identified as the major CCHS-causing gene?', [F('G',9,'PHOX2B was identified as the major CCHS-causing gene for patients in 2003.','2003, as reported by the guideline.')],[]),
('Which name does the guideline give to CCHS accompanied by Hirschsprung disease?', [F('G',24,'CCHS with Hirschsprung disease (known as Haddad Syndrome)','Haddad Syndrome.')],[]),
],
'paraphrase':[
('Was the Italian analysis based on a randomized experiment or on looking back at patient records?', [F('I',19,'collected retrospectively','A retrospective analysis.'),F('I',21,'review of the electronic medical record','Used electronic medical records.')],[]),
('Did the guideline authors rely entirely on high-certainty trials when drafting recommendations?', [F('G',13,'most of the evidence is descriptive and of low grade of recommendation','Mostly descriptive evidence of low recommendation grade.'),F('G',13,'a blend of published evidence and clinical experience','Combined publications and clinical experience.')],[]),
('How do the Italian data illustrate care changing as a team gained experience?', [F('I',20,'14 patients have been followed in our Pediatric Intermediate Care Unit (PICU) since the onset of symptoms','14 followed in PICU from symptom onset.'),F('I',20,'The remaining 8 patients were initially treated by the staff of the Intensive Care Unit','Eight initially treated in ICU.')],[]),
('Can a researcher tag every NPARM case as having uniformly severe respiratory disease?', [F('G',53,'some of whom may have only mild hypoventilation','Some NPARM cases may have mild hypoventilation.'),F('G',53,'Hypoventilation may not be the main feature in some PHOX2B mutations.','Hypoventilation need not be the main feature.')],[]),
('Does repeat length invariably determine how much ventilatory support is needed?', [F('G',52,'although this is inconsistent','The described genotype relationship is inconsistent.')],[F('G',52,'this relationship is variable and a few remarkable exceptions are known','Variability and exceptions must be retained.')]),
('Why should the ventilation choices in the Italian study not be attributed only to genotype?', [F('I',58,'but also by management habits in 6 children born before 2010','Management habits affected six pre-2010 children.')],[F('I',58,'It is probable that the brain damage due to HIE contributed','HIE was proposed as a contributor, not established as the sole cause.')]),
('What does the review say about gene deletions as an uncommon CCHS category?', [F('R',10,'Partial or whole gene deletions of PHOX2B account for <1% cases','Partial or whole PHOX2B deletions account for under 1%.')],[F('R',10,'are associated with variable phenotypes','Variable phenotypes.')]),
('Does later presentation mean only childhood presentation in the guideline classification?', [F('G',22,'or in childhood or adulthood','Later onset also includes adulthood.')],[]),
('How does the guideline distinguish the two levels of respiratory phenotype by duration?', [F('G',23,'(i) sleep hypoventilation; (ii) 24','Sleep-only versus 24-hour hypoventilation.')],[]),
('How were the apparently asymptomatic adult women in the Italian discussion eventually identified?', [F('I',55,'received the diagnosis after confirmation of the disease in their offspring','After confirmation in their offspring.')],[F('I',55,'Only two asymptomatic female patients','Observation concerns two women.')]),
],
'exact_identifiers':[
('Where does the 2022 review locate PHOX2B, and how many exons does it describe?', [F('R',10,'chromosome 4p12 and has 3 exons','Chromosome 4p12; three exons.')],[]),
('Which PARM genotype identifiers were common in the Italian molecular analysis?', [F('I',32,'PARMs (20/25, 20/26, and 20/27)','20/25, 20/26 and 20/27.')],[]),
('What observation does the Italian report connect specifically to c.780dupT and neural crest tumor?', [F('I',67,'one child with c.780dupT mutation','A neural crest tumor was detected in one child carrying c.780dupT.')],[F('I',67,'one child','Single observed child; not a population effect estimate.')]),
('Which gene symbols accompany MYO1H in the guideline additional-gene paragraph?', [F('G',60,'MYO1H and LBX1','LBX1 is paired with MYO1H.')],[F('G',60,'two consanguineous families','Evidence described concerns two consanguineous families.')]),
('What does the guideline identify as RET and ECE1?', [F('G',61,'receptor tyrosine kinase (RET), and endothelin converting enzyme 1 (ECE1)','RET: receptor tyrosine kinase; ECE1: endothelin converting enzyme 1.')],[]),
('Which exon and repeat counts does the guideline associate with PHOX2B PARMs?', [F('G',49,'in the exon 3','Exon 3.'),F('G',49,'20 repeats','Normally 20 repeats.'),F('G',49,'24 to 33 repeats','Affected allele 24–33 repeats.')],[]),
('Which repeat-genotype range does the 2022 review describe for PARMs?', [F('R',10,'20/24 – 20/33','20/24–20/33.')],[]),
('Which G47.35, MIM and ORPHA identifiers are listed together in the guideline?', [F('G',8,'G47.35; MIM 209880, ORPHA 661','G47.35; MIM 209880; ORPHA 661.')],[]),
('Which ICSD version and publication year accompany the PHOX2B classification statement?', [F('G',9,'version 3 published in 2014','International Classification of Sleep Disorders version 3, 2014.')],[]),
('Which frameshift mutation strings are written in the Italian discussion?', [F('I',56,'C.225_256delCT, c.780dupT','Preserve the reported strings C.225_256delCT and c.780dupT.')],[F('I',56,'C.225–256delCT','The paragraph also uses a different dash-form spelling; do not silently normalize HGVS nomenclature.')]),
],
'comparison':[
('Contrast the Italian study design with the guideline evidence-development method.', [F('I',19,'collected retrospectively','Italian study: retrospective patient data.'),F('G',13,'a blend of published evidence and clinical experience','Guideline: published evidence blended with clinical experience.')],[]),
('Compare the PARM fraction in the Italian cohort with the general estimate in the 2022 review.', [F('I',32,'19/22 cases (86%)','Italian cohort 86%.'),F('R',10,'account for 90% of CCHS cases','Review general estimate 90%.')],[F('I',32,'19/22 cases','Different evidence bases; the small cohort is not a replacement prevalence estimate.')]),
('Compare how the guideline and review qualify genotype–phenotype associations.', [F('G',52,'this relationship is variable','Guideline: variable relationship.'),F('R',11,'variable expression and incomplete penetrance','Review: variable expression and incomplete penetrance.')],[]),
('Compare the Italian observation and guideline account concerning severity with NPARMs.', [F('I',49,'NPARMs are more likely to have more severe disease','Italian account describes greater likelihood of severity.'),F('G',53,'some of whom may have only mild hypoventilation','Guideline includes mild cases.')],[F('G',53,'wide spectrum of phenotypes','A spectrum, not a universal deterministic rule.')]),
('How do the Italian limitations and guideline evidence grade constrain research conclusions?', [F('I',68,'retrospective design, the poor sample','Italian retrospective/small-sample limitation.'),F('G',13,'most of the evidence is descriptive','Guideline mostly descriptive evidence.')],[]),
('Compare the guideline and review descriptions of rare PHOX2B deletions.', [F('G',50,'mainly large deletions','Guideline includes large deletions.'),F('R',10,'Partial or whole gene deletions','Review includes partial or whole deletions.')],[F('R',10,'variable phenotypes','Variable phenotypes; neither passage justifies a uniform phenotype.')]),
('Compare the Italian study aim with the guideline purpose regarding change over time.', [F('I',17,'changing strategy in the management','Italian aim: changing management strategy.'),F('G',14,'clinical features of the condition continue to change','Guideline must be read in context of evolving clinical features.')],[]),
('Compare sleep-stage and waking hypoventilation descriptions in the guideline and 2022 review.', [F('G',19,'more severe during sleep than during wakefulness','Guideline: worse during sleep.'),F('R',7,'worse during nonrapid eye movement (NREM) sleep than during rapid eye movement (REM) sleep','Review: worse in NREM than REM.')],[]),
('Compare the guideline description of transmission probability with its qualification about expression in offspring.', [F('G',58,'50% risk for transmitting the mutation','Reported transmission probability 50%.'),F('G',58,'depends on the penetrance of the mutation transmitted','Expression depends on penetrance.')],[F('G',58,'incomplete penetrance or very mild manifestations','Transmission is not a promise of identical clinical severity.')]),
('How do the Italian results and discussion describe detection of the two adult women?', [F('I',28,'at 35 and 38 years','Results provide ages 35 and 38.'),F('I',55,'after confirmation of the disease in their offspring','Discussion links identification to offspring.')],[]),
],
'limitations':[
('What qualification must accompany a tag linking longer repeats with continuous ventilation?', [F('G',52,'although this is inconsistent','Relationship is inconsistent.')],[F('G',52,'a few remarkable exceptions','Known exceptions must be included.')]),
('May the Italian retrospective findings be presented as randomized causal evidence?', [F('I',68,'retrospective design','No; retrospective design.')],[F('I',68,'heterogeneity of the described population','Heterogeneous population restricts interpretation.')]),
('What does the Italian epilepsy paragraph say about a genotype correlation?', [F('I',61,'no correlation between epilepsy and genotype was finally seen','No correlation was observed in that sample.')],[F('I',61,'Three of our patients','Only three cases; not proof of no association in all CCHS.')]),
('How should the Italian authors suggestion about hypoxia and behavior be qualified?', [F('I',62,'It seems that the psychological development','Tentative author interpretation.')],[F('I',62,'influenced by hypoxia rather than the genotype','Do not upgrade the proposed influence to proven causation.')]),
('What prevents the guideline recommendations from being labeled entirely trial-proven?', [F('G',13,'combined with clinical expertise as required','Clinical expertise supplements published evidence.')],[F('G',13,'low grade of recommendation','Evidence recommendation grade is described as low.')]),
('Does the guideline additional-gene passage claim all unexplained CCHS cases are genetically solved?', [F('G',60,'without any identified gene mutations','No; a subset has no identified gene mutation.')],[F('G',60,'yet unknown genes','Unknown genes remain.')]),
('Can the review NPARM description justify assuming identical disease in every carrier?', [F('R',11,'clinical variability','No, clinical variability is described.')],[F('R',11,'variable expression and incomplete penetrance','Preserve variability and incomplete penetrance.')]),
('Does the mother–son observation in the Italian discussion prove environmental cofactors caused the difference?', [F('I',56,'This observation suggests','The authors present a suggestion.')],[F('I',56,'somatic mosaicism or unknown environmental cofactors could influence','Possible explanations, not proven causal attribution.')]),
('Can the guideline supply an exact recurrence percentage for proven somatic mosaicism?', [F('G',57,'less than 50%','Described as less than 50%.')],[F('G',57,'not quantifiable risk of recurrence','The risk is not quantified exactly.')]),
('Does the guideline advocate PHOX2B testing for BRUE without hypoventilation?', [F('G',47,'We do not advocate testing for PHOX2B','No.')],[F('G',47,'without hypoventilation','The absence of hypoventilation is an essential qualification.')]),
],
'absent':[(q,[],[]) for q in [
'What measured results does the 2021 Italian study report from a randomized PHOX2B gene-editing intervention?',
'Which downloadable patient-level transcriptomic accession belongs to the Italian retrospective cohort?',
'What sensitivity and specificity did these papers measure for this Evidence Navigator software?',
'What experiment in the guideline proves that every NPARM variant has the same effect size?',
'Which clinical trial completed in 2026 is reported by these 2020–2022 source publications?',
'What approved research-registry identifier was assigned to each tag proposed by this application?',
'What exact universal effect size for CCHS treatment can be obtained from these heterogeneous sources?',
'What results does the 2022 review report for a prospective trial completed in 2025?',
'What is the DOI of an unpublished laboratory experiment conducted yesterday by our team?',
'Which researcher has clinically validated the answers produced by this application?'
]]}

def build(config=None):
    docs,excluded,manifest=prepare(cfg=config or load_config())
    questions=[]; seen_passages={}
    for category, items in rows.items():
        assert len(items)==10,category
        for i,(question,facts,qualifications) in enumerate(items):
            split='tuning' if i<7 else 'test'
            refs=[]; required=[]; quals=[]
            for specs,destination in [(facts,required),(qualifications,quals)]:
                for sid,passage,quote,text in specs:
                    key=(sid,passage)
                    if seen_passages.setdefault(key,split)!=split: raise ValueError(('Reference-passage leakage',key))
                    hits=[d for d in docs if d['source_id']==sid and d['passage_index']==passage and quote in d['content']]
                    if not hits: raise ValueError(('Unresolvable reference',sid,passage,quote))
                    ref={'id':hits[0]['id'],'quote':quote,'source_id':sid,'source_version':hits[0]['source_version'],'passage_index':passage,'acceptable_ids':[h['id'] for h in hits]}
                    index=len(refs);refs.append(ref);destination.append({'text':text,'reference_indices':[index]})
            qid=category[:3].upper()+f'-{i+1:02d}'
            questions.append({'schema_version':2,'id':qid,'slice':category,'group_id':qid,'split':split,'question':question,
                'answerable':bool(facts),'relevant_ids':sorted({x for r in refs for x in r['acceptable_ids']}),
                'reference_quotes':refs,'required_facts':required,'required_qualifications':quals,
                'abstention_reason':'' if facts else 'The requested result, artifact, date or validation is not established by this frozen three-publication corpus. Do not infer absence from all literature.',
                'label_status':'ASSISTANT_AUTHORED_PROVISIONAL_NOT_HUMAN_VALIDATED'})
    validate_questions(questions,docs)
    bank={'schema_version':2,'corpus_id':digest(docs),'manifest_hash':digest(manifest),'questions':questions,
        'design':'60 questions; six slices; 42 tuning/18 test. Project design, not a course threshold.',
        'limitations':['Assistant-authored source-anchored references; no biomedical expert validation.','Source-passage groups are separated across tuning/test, but broad topics and publications overlap.','Synthetic questions may favor source wording; this is not a representative user study.','Legacy 13 questions were previously exposed and remain regression-only.','Hit/MRR measures any reference hit; multi-fact coverage is evaluated separately.']}
    return bank

if __name__=='__main__':
    bank=build();write_json(ROOT/'data/evaluation/questions-v2.json',bank)
    print({'questions':len(bank['questions']),'corpus_id':bank['corpus_id'],'bank_hash':digest(bank)})
