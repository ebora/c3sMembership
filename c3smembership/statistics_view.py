from pyramid.view import view_config
from c3smembership.models import (
    C3sMember,
    C3sStaff,
    Shares,
    Dues15Invoice,
)

@view_config(renderer='templates/stats.pt',
             permission='manage',
             route_name='stats')
def stats_view(request):
    """
    This view lets accountants view statistics:
    how many membership applications, real members, shares, etc.
    """
    #countries_dict = C3sMember.get_countries_list()
    _cl = C3sMember.get_countries_list()
    _cl_sorted = _cl.items()
    #print "die liste: {}".format(_cl_sorted)
    import operator
    _cl_sorted.sort(key=operator.itemgetter(1), reverse=True)
    #print "sortiert: {}".format(_cl_sorted)
    return {
        # form submissions
        '_number_of_datasets': C3sMember.get_number(),
        'afm_shares_unpaid': C3sMember.afm_num_shares_unpaid(),
        'afm_shares_paid': C3sMember.afm_num_shares_paid(),
        # shares
        #'num_shares': C3sMember.get_total_shares(),
        'num_shares_members': Shares.get_total_shares(),
        #'num_shares_mem_norm': Shares.get_sum_norm(),
        #'num_shares_mem_inv': Shares.get_sum_inv(),

        # memberships
        'num_members_accepted': C3sMember.get_num_members_accepted(),
        'num_non_accepted': C3sMember.get_num_non_accepted(),
        'num_nonmember_listing': C3sMember.nonmember_listing_count(),
        'num_duplicates': len(C3sMember.get_duplicates()),
        #'num_empty_slots': C3sMember.get_num_empty_slots(),
        # normal persons vs. legal entities
        'num_ms_nat_acc': C3sMember.get_num_mem_nat_acc(),
        'num_ms_jur_acc': C3sMember.get_num_mem_jur_acc(),
        # normal vs. investing memberships
        'num_ms_norm': C3sMember.get_num_mem_norm(),
        'num_ms_inves': C3sMember.get_num_mem_invest(),
        'num_ms_features': C3sMember.get_num_mem_other_features(),
        # membership_numbers
        'num_memnums': C3sMember.get_num_membership_numbers(),
        'max_memnum': C3sMember.get_highest_membership_number(),
        'next_memnum': C3sMember.get_next_free_membership_number(),

        # countries
        'num_countries': C3sMember.get_num_countries(),
        'countries_list': _cl_sorted,
        #    key=lambda x: x[1]
        #),  # XXX TODO: sorte

        # dues stats
        'dues_stats': Dues15Invoice.get_monthly_stats(),

        # staff figures
        'num_staff': len(C3sStaff.get_all())
    }
