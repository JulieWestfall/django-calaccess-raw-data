from django.db import models

# Create your models here.
class Filer(models.Model):
    FILER_TYPE_OPTIONS =(
        ('pac', 'Political Action Committee'),
        ('cand', 'Candidate'),
    )
    filer_id = models.IntegerField()
    xref_filer_id = models.CharField(max_length=32L)
    name = models.CharField(max_length=255L, null=True)
    filer_type = models.CharField(max_length=10L, choices=FILER_TYPE_OPTIONS)

class Committee(models.Model):
    CMTE_TYPE_OPTIONS = (
        ('mdid', 'Major Donor / Independent Expenditure'),
        ('sm', 'Slate Mailer'),
        ('bi', 'Ballot Initiative'),
        ('cc', 'Candidate Committee'),
    )
    filer = models.ForeignKey(Filer)
    filer_id_raw = models.IntegerField()
    name = models.CharField(max_length=255, blank=True)
    committee_type = models.CharField(max_length=4, choices=CMTE_TYPE_OPTIONS)

class CandidateCommittee(models.Model):
    committee = models.ForeignKey(Committee)
    filer = models.ForeignKey(Filer)
    filer_id_raw = models.IntegerField()
    xref_filer_id_raw = models.CharField(max_length=32L)
    name = models.CharField(max_length=255)

class Cycle(models.Model):
    name = models.IntegerField()

class Summary(models.Model):
    cycle = models.ForeignKey(Cycle)
    committee = models.ForeignKey(Committee)
    


class Expenditure(models.Model):
    '''
    This is a condensed version of the Raw CAL-ACCESS EXPN_CD table
    It leaves out a lot of the supporting information for the expense
    Like jurisdiction info, ballot initiative info, treasurer info, support/opposition info, etc.
    This just pulls in who got paid and how much
    And tries to prep the data for categorization by orgs and individuals
    Data comes from calaccess.models.ExpnCd
    '''
    cycle = models.ForeignKey(Cycle)
    committee = models.ForeignKey(Committee)
    
    ## Raw data fields
    amend_id = models.IntegerField()
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    bakref_tid = models.CharField(max_length=10L, blank=True)
    cmte_id = models.CharField(max_length=9L, blank=True)
    cum_other = models.DecimalField(max_digits=16, decimal_places=2)
    cum_ytd = models.DecimalField(max_digits=16, decimal_places=2)
    entity_cd = models.CharField(max_length=5L, blank=True)
    expn_chkno = models.CharField(max_length=20L, blank=True)
    expn_code = models.CharField(max_length=3L, blank=True)
    expn_date = models.DateField()
    expn_dscr = models.CharField(max_length=400L, blank=True)
    filing_id = models.IntegerField()
    form_type = models.CharField(max_length=6L, blank=True)
    g_from_e_f = models.CharField(max_length=1L, blank=True) # back reference from Form 460 Schedule G to Schedule E or F
    line_item = models.IntegerField()
    memo_code = models.CharField(max_length=1L, blank=True)
    memo_refno = models.CharField(max_length=20L, blank=True)
    payee_adr1 = models.CharField(max_length=55L, blank=True)
    payee_adr2 = models.CharField(max_length=55L, blank=True)
    payee_city = models.CharField(max_length=30L, blank=True)
    payee_namf = models.CharField(max_length=5L, blank=True)
    payee_naml = models.CharField(max_length=200L, blank=True)
    payee_nams = models.CharField(max_length=10L, blank=True)
    payee_namt = models.CharField(max_length=10L, blank=True)
    payee_namst = models.CharField(max_length=2L, blank=True)
    payee_zip4 = models.CharField(max_length=10L, blank=True)
    tran_id = models.CharField(max_length=20L, blank=True)
    xref_match = models.CharField(max_length=1L, blank=True) # a related item on other schedule has the same transaction identifier. "X" indicates this condition is true
    xref_schnm = models.CharField(max_length=2L, blank=True) # Related record is included on Form 460 Schedules B2 or F
    
    ## Derived fields
    name = models.CharField(max_length=255) # derive like so (e.payee_namt + ' '+ e.payee_namf + ' ' + e.payee_naml + ' ' + e.payee_nams).strip()
    status = models.BooleanField(default=True) # False meanse they are duplicated, additional disclosure that shouldn't be used for summing up but provide addtional info on the transaction
    org_id = models.IntegerField(default=None, null=True)
    individual_id = models.IntegerField(default=None, null=True)
    
    def raw(self):
        try:
            from calaccess.models import ExpnCd
            obj = ExpnCd.objects.get(amend_id=self.amend_id, filing_id=self.filing_id, tran_id=self.tran_id, bakref_tid=self.bakref_tid)
        except:
            print 'Raw data not available. Install calaccess app to process and house raw data.'
            obj = None
        return obj

class Contribution(models.Model):
    cycle = models.ForeignKey(Cycle)
    committee = models.ForeignKey(Committee)
    
    ## Raw data fields
    amend_id = models.IntegerField()
    amount = models.DecimalField(decimal_places=2, max_digits=14, db_column='AMOUNT')
    bakref_tid = models.CharField(max_length=20L, blank=True)
    cmte_id = models.CharField(max_length=9L, blank=True)
    ctrib_adr1 = models.CharField(max_length=55L, blank=True)
    ctrib_adr2 = models.CharField(max_length=55L, blank=True)
    ctrib_city = models.CharField(max_length=30L, blank=True)
    ctrib_dscr = models.CharField(max_length=90L, blank=True)
    ctrib_emp = models.CharField(max_length=200L, blank=True)
    ctrib_namf = models.CharField(max_length=45L, blank=True)
    ctrib_naml = models.CharField(max_length=200L, )
    ctrib_nams = models.CharField(max_length=10L, blank=True)
    ctrib_namt = models.CharField(max_length=10L, blank=True)
    ctrib_occ = models.CharField(max_length=60L, blank=True)
    ctrib_self = models.CharField(max_length=1L, blank=True)
    ctrib_st = models.CharField(max_length=2L, blank=True)
    ctrib_zip4 = models.CharField(max_length=10L, blank=True)
    cum_oth = models.DecimalField(decimal_places=2, null=True, max_digits=14, blank=True)
    cum_ytd = models.DecimalField(decimal_places=2, null=True, max_digits=14, blank=True)
    date_thru = models.DateField(null=True, blank=True)
    entity_cd = models.CharField(max_length=3L)
    filing_id = models.IntegerField()
    form_type = models.CharField(max_length=9L)
    intr_adr1 = models.CharField(max_length=55L, blank=True)
    intr_adr2 = models.CharField(max_length=55L, blank=True)
    intr_city = models.CharField(max_length=30L, blank=True)
    intr_cmteid = models.CharField(max_length=9L, blank=True)
    intr_emp = models.CharField(max_length=200L, blank=True)
    intr_namf = models.CharField(max_length=45L, blank=True)
    intr_naml = models.CharField(max_length=200L, blank=True)
    intr_nams = models.CharField(max_length=10L, blank=True)
    intr_namt = models.CharField(max_length=10L, blank=True)
    intr_occ = models.CharField(max_length=60L, blank=True)
    intr_self = models.CharField(max_length=1L, blank=True)
    intr_st = models.CharField(max_length=2L, blank=True)
    intr_zip4 = models.CharField(max_length=10L, blank=True)
    line_item = models.IntegerField()
    memo_code = models.CharField(max_length=1L, blank=True)
    memo_refno = models.CharField(max_length=20L, blank=True)
    rcpt_date = models.DateField()
    rec_type = models.CharField(max_length=4L)
    tran_id = models.CharField(max_length=20L)
    tran_type = models.CharField(max_length=1L, blank=True)
    xref_match = models.CharField(max_length=1L, blank=True)
    xref_schnm = models.CharField(max_length=2L, blank=True)
    
    ## Derived fields
    name = models.CharField(max_length=255) # derive like so (r.ctrib_namt + ' '+ r.ctrib_namf + ' ' + r.ctrib_naml + ' ' + r.ctrib_nams).strip()
    status = models.BooleanField(default=True) # False meanse they are duplicated, additional disclosure that shouldn't be used for summing up but provide addtional info on the transaction
    org_id = models.IntegerField(default=None, null=True)
    individual_id = models.IntegerField(default=None, null=True)
    
    def raw(self):
        try:
            from calaccess.models import RcptCd
            obj = RcptCd.objects.get(amend_id=self.amend_id, filing_id=self.filing_id, tran_id=self.tran_id, bakref_tid=self.bakref_tid)
        except:
            print 'Raw data not available. Install calaccess app to process and house raw data.'
            obj = None
        return obj
    