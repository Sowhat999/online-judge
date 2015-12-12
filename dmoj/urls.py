from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap
from social.apps.django_app.urls import urlpatterns as social_auth_patterns

from judge import views
from judge.feed import CommentFeed, AtomCommentFeed, BlogFeed, AtomBlogFeed, ProblemFeed, AtomProblemFeed
from judge.forms import CustomAuthenticationForm
from judge.rabbitmq import views as rabbitmq_views
from judge.sitemap import ProblemSitemap, UserSitemap, HomePageSitemap, UrlSitemap, ContestSitemap, OrganizationSitemap, \
    BlogPostSitemap, SolutionSitemap
from judge.views import RegistrationView, ActivationView, TemplateView
from judge.views import organization, language, status, blog, problem, solution, mailgun, license, register, user, submission, widgets, comment, contests, api
from judge.views.select2 import UserSelect2View, OrganizationSelect2View, ProblemSelect2View, CommentSelect2View, \
        ContestProfileSelect2View

admin.autodiscover()

register_patterns = [
    url(r'^activate/complete/$',
        TemplateView.as_view(template_name='registration/activation_complete.jade',
                             title='Activation Successful!'),
        name='registration_activation_complete'),
    # Activation keys get matched by \w+ instead of the more specific
    # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
    # that way it can return a sensible "invalid key" message instead of a
    # confusing 404.
    url(r'^activate/(?P<activation_key>\w+)/$',
        ActivationView.as_view(title='Activation key invalid'),
        name='registration_activate'),
    url(r'^register/$',
        RegistrationView.as_view(title='Register'),
        name='registration_register'),
    url(r'^register/complete/$',
        TemplateView.as_view(template_name='registration/registration_complete.jade',
                             title='Registration Completed'),
        name='registration_complete'),
    url(r'^register/closed/$',
        TemplateView.as_view(template_name='registration/registration_closed.html',
                             title='Registration not allowed'),
        name='registration_disallowed'),
    url(r'^login/$', auth_views.login,
        {'template_name': 'registration/login.jade', 'extra_context': {'title': 'Login'},
         'authentication_form': CustomAuthenticationForm},
        name='auth_login'),
    url(r'^logout/$',
        auth_views.logout,
        {'template_name': 'registration/logout.jade', 'extra_context': {'title': 'You have been successfully logged out.'}},
        name='auth_logout'),
    url(r'^password/change/$',
        auth_views.password_change,
        {'template_name': 'registration/password_change_form.jade', 'extra_context': {'title': 'Change Password'}},
        name='password_change'),
    url(r'^password/change/done/$',
        auth_views.password_change_done,
        {'template_name': 'registration/password_change_done.jade', 'extra_context': {'title': 'Password Changed'}},
        name='password_change_done'),
    url(r'^password/reset/$',
        auth_views.password_reset,
        {'template_name': 'registration/password_reset.jade', 'extra_context': {'title': 'Reset Password'},
         'html_email_template_name': 'registration/password_reset_email.html',
         'email_template_name': 'registration/password_reset_email.txt'},
        name='password_reset'),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        auth_views.password_reset_confirm,
        {'template_name': 'registration/password_reset_confirm.jade', 'extra_context': {'title': 'Confirm Reset Password'}},
        name='password_reset_confirm'),
    url(r'^password/reset/complete/$',
        auth_views.password_reset_complete,
        {'template_name': 'registration/password_reset_complete.jade', 'extra_context': {'title': 'Password Reset Complete'}},
        name='password_reset_complete'),
    url(r'^password/reset/done/$',
        auth_views.password_reset_done,
        {'template_name': 'registration/password_reset_done.jade', 'extra_context': {'title': 'Password Reset Successful'}},
        name='password_reset_done'),
    url(r'^social/error/$', register.social_auth_error, name='social_auth_error'),
]


def exception(request):
    raise RuntimeError('@Xyene asked me to cause this')


urlpatterns = [
    url(r'^$', blog.PostList.as_view(template_name='home.jade', title='Home'), kwargs={'page': 1}, name='home'),
    url(r'^500/$', exception),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include(register_patterns)),
    url('', include(social_auth_patterns, namespace='social')),

    url(r'^users/$', user.users),
    url(r'^user/(?P<username>\w+)$', views.UserAboutPage.as_view(), name='user_page'),
    url(r'^user/(?P<username>\w+)/solved$', views.UserProblemsPage.as_view(), name='user_problems'),
    url(r'^user$', views.UserAboutPage.as_view(), name='user_page'),
    url(r'^edit/profile/$', user.edit_profile),

    url(r'^problems/$', problem.ProblemList.as_view(), name='problem_list'),
    url(r'^problems/own/$', problem.OwnProblemList.as_view(), name='own_problem_list'),
    url(r'^problems/random/$', problem.random_problem, name='problem_random'),
    url(r'^problem/(?P<code>[^/]+)$', problem.ProblemDetail.as_view(), name='problem_detail'),
    url(r'^problem/(?P<code>[^/]+)/raw$', problem.ProblemRaw.as_view(), name='problem_raw'),
    url(r'^problem/(?P<code>[^/]+)/pdf$', problem.ProblemPdfView.as_view(), name='problem_pdf'),
    url(r'^problem/(?P<code>[^/]+)/latex$', problem.ProblemLatexView.as_view(), name='problem_latex'),
    url(r'^problem/(?P<code>[^/]+)/clone', problem.clone_problem, name='problem_clone'),
    url(r'^problem/([^/]+)/submit$', problem.problem_submit),
    url(r'^problem/([^/]+)/resubmit/(\d+)$', problem.problem_submit),

    url(r'^submit/problem/$', problem.problem_submit),
    url(r'^rejudge$', widgets.rejudge_submission),
    url(r'^src/(?P<pk>\d+)$', views.SubmissionSource.as_view(), name='submission_source'),
    url(r'^submission/(?P<pk>\d+)$', views.SubmissionStatus.as_view(), name='submission_status'),
    url(r'^submission/(\d+)/abort$', submission.abort_submission),
    url(r'^submission/(\d+)/html$', submission.single_submission),

    url(r'^submissions/$', views.AllSubmissions.as_view(), name='all_submissions'),
    url(r'^submissions/(?P<page>\d+)$', views.AllSubmissions.as_view(), name='all_submissions'),

    url(r'^problem/(?P<problem>\w+)/', include([
        url(r'^rank/$', views.RankedSubmissions.as_view(), name='ranked_submissions'),
        url(r'^rank/(?P<page>\d+)$', views.RankedSubmissions.as_view(), name='ranked_submissions'),
        url(r'^submissions/$', views.ProblemSubmissions.as_view(), name='chronological_submissions'),
        url(r'^submissions/(?P<page>\d+)$', views.ProblemSubmissions.as_view(), name='chronological_submissions'),
        url(r'^submissions/(?P<user>\w+)/$', views.UserProblemSubmissions.as_view(), name='user_submissions'),
        url(r'^submissions/(?P<user>\w+)/(?P<page>\d+)$', views.UserProblemSubmissions.as_view(), name='user_submissions'),
    ])),

    url(r'^user/(?P<user>\w+)/submissions/$', views.AllUserSubmissions.as_view(), name='all_user_submissions'),
    url(r'^user/(?P<user>\w+)/submissions/(?P<page>\d+)$', views.AllUserSubmissions.as_view(), name='all_user_submissions'),

    url(r'^single_submission', submission.single_submission_query),
    url(r'^submission_testcases', views.SubmissionTestCaseQuery.as_view(), name='submission_testcases_query'),

    url(r'^comments/upvote/$', comment.upvote_comment),
    url(r'^comments/downvote/$', comment.downvote_comment),
    url(r'^comments/(?P<id>\d+)/', include([
        url(r'^revisions$', views.CommentHistory.as_view(), name='comment_history'),
        url(r'^edit$', views.CommentEdit.as_view(), name='comment_edit'),
        url(r'^revisions/ajax$', views.CommentHistoryAjax.as_view(), name='comment_history_ajax'),
        url(r'^edit/ajax$', views.CommentEditAjax.as_view(), name='comment_edit_ajax'),
        url(r'^render$', views.CommentContent.as_view(), name='comment_content'),
    ])),

    url(r'^contests/$', views.ContestList.as_view(), name='contest_list'),
    url(r'^contests/(?P<year>\d+)/(?P<month>\d+)/$', views.ContestCalendar.as_view(), name='contest_calendar'),
    url(r'^contest/(?P<key>\w+)$', views.ContestDetail.as_view(), name='contest_view'),
    url(r'^contest/(\w+)/ranking/$', contests.contest_ranking, name='contest_ranking'),
    url(r'^contest/(\w+)/ranking/ajax$', contests.contest_ranking_ajax, name='contest_ranking_ajax'),
    url(r'^contest/(?P<key>\w+)/join$', views.ContestJoin.as_view(), name='contest_join'),
    url(r'^contest/(?P<key>\w+)/leave$', views.ContestLeave.as_view(), name='contest_leave'),

    url(r'^contest/(?P<contest>\w+)/rank/(?P<problem>\w+)/$', views.ContestRankedSubmission.as_view(), name='contest_ranked_submissions'),
    url(r'^contest/(?P<contest>\w+)/rank/(?P<problem>\w+)/(?P<page>\d+)$', views.ContestRankedSubmission.as_view(), name='contest_ranked_submissions'),

    url(r'^contest/(?P<contest>\w+)/submissions/(?P<user>\w+)/(?P<problem>\w+)/$', views.UserContestSubmissions.as_view(), name='contest_user_submissions'),
    url(r'^contest/(?P<contest>\w+)/submissions/(?P<user>\w+)/(?P<problem>\w+)/(?P<page>\d+)$', views.UserContestSubmissions.as_view(), name='contest_user_submissions'),

    url(r'^organizations/$', organization.OrganizationList.as_view(), name='organization_list'),
    url(r'^organization/(?P<key>\w+)$', organization.OrganizationHome.as_view(), name='organization_home'),
    url(r'^organization/(?P<key>\w+)/users$', organization.OrganizationUsers.as_view(), name='organization_users'),
    url(r'^organization/(?P<key>\w+)/join$', organization.JoinOrganization.as_view(), name='join_organization'),
    url(r'^organization/(?P<key>\w+)/leave$', organization.LeaveOrganization.as_view(), name='leave_organization'),
    url(r'^organization/(?P<key>\w+)/edit$', organization.EditOrganization.as_view(), name='edit_organization'),
    url(r'^organization/(?P<key>\w+)/request$', organization.RequestJoinOrganization.as_view(), name='request_organization'),
    url(r'^organization/(?P<key>\w+)/request/(?P<pk>\d+)$', organization.OrganizationRequestDetail.as_view(), name='request_organization_detail'),
    url(r'^organization/(?P<key>\w+)/requests/pending$', organization.OrganizationRequestView.as_view(), name='organization_requests_pending'),
    url(r'^organization/(?P<key>\w+)/requests/log$', organization.OrganizationRequestLog.as_view(), name='organization_requests_log'),
    url(r'^organization/(?P<key>\w+)/requests/approved$', organization.OrganizationRequestLog.as_view(states=('A',), tab='approved'), name='organization_requests_approved'),
    url(r'^organization/(?P<key>\w+)/requests/rejected$', organization.OrganizationRequestLog.as_view(states=('R',), tab='rejected'), name='organization_requests_rejected'),

    url(r'^runtimes/$', language.LanguageList.as_view(), name='runtime_list'),
    url(r'^runtime/(?P<key>\w+)$', language.LanguageDetail.as_view(), name='runtime_info'),
    url(r'^runtime/(?P<key>\w+)/judges$', language.LanguageJudgesAjaxList.as_view(), name='runtime_judge_ajax'),

    url(r'^status/$', status.status_all),
    url(r'^status-table/$', status.status_table),
    url(r'^judge/(?P<name>[\w.]+)$', status.JudgeDetail.as_view(), name='judge_info'),

    url(r'^api/contest/list$', api.api_contest_list),
    url(r'^api/problem/list$', api.api_problem_list),
    url(r'^api/problem/info/(\w+)', api.api_problem_info),
    url(r'^api/user/list', api.api_user_list),
    url(r'^api/user/info/(\w+)', api.api_user_info),
    url(r'^api/user/submissions/(\w+)', api.api_user_submissions),
    url(r'^api/judge/auth/rabbitmq/user$', rabbitmq_views.auth_user),
    url(r'^api/judge/auth/rabbitmq/vhost$', rabbitmq_views.auth_vhost),
    url(r'^api/judge/auth/rabbitmq/resource$', rabbitmq_views.auth_resource),

    url(r'^blog/$', blog.PostList.as_view(), name='blog_post_list'),
    url(r'^blog/(?P<page>\d+)$', blog.PostList.as_view(), name='blog_post_list'),
    url(r'^post/(?P<id>\d+)-(?P<slug>.*)$', blog.PostView.as_view(), name='blog_post'),

    url(r'^solution/(?P<url>.*)$', solution.SolutionView.as_view(), name='solution'),
    url(r'^license/(?P<key>[-\w.]+)$', license.LicenseDetail.as_view(), name='license'),

    url(r'^mailgun/mail_activate/$', mailgun.MailgunActivationView.as_view(), name='mailgun_activate'),
    url(r'^detect_timezone$', views.DetectTimezone.as_view(), name='detect_timezone'),

    url(r'^feed/', include([
        url(r'^problems/rss/$', ProblemFeed(), name='problem_rss'),
        url(r'^problems/atom/$', AtomProblemFeed(), name='problem_atom'),
        url(r'^comment/rss/$', CommentFeed(), name='comment_rss'),
        url(r'^comment/atom/$', AtomCommentFeed(), name='comment_atom'),
        url(r'^blog/rss/$', BlogFeed()),
        url(r'^blog/atom/$', AtomBlogFeed()),
    ])),

    url(r'^sitemap\.xml$', sitemap, {'sitemaps': {
        'problem': ProblemSitemap,
        'user': UserSitemap,
        'home': HomePageSitemap,
        'contest': ContestSitemap,
        'organization': OrganizationSitemap,
        'blog': BlogPostSitemap,
        'solutions': SolutionSitemap,
        'pages': UrlSitemap([
            {'location': '/about/', 'priority': 0.9},
        ]),
    }}),

    url(r'^judge-select2/', include([
        url(r'^profile/', UserSelect2View.as_view(), name='profile_select2'),
        url(r'^organization/', OrganizationSelect2View.as_view(), name='organization_select2'),
        url(r'^problem/', ProblemSelect2View.as_view(), name='problem_select2'),
        url(r'^comment/', CommentSelect2View.as_view(), name='comment_select2'),
        url(r'^contest_profile/', ContestProfileSelect2View.as_view(), name='contest_profile_select2'),
    ])),
]

handler404 = 'judge.views.error.error404'
handler403 = 'judge.views.error.error403'
handler500 = 'judge.views.error.error500'

if 'tinymce' in settings.INSTALLED_APPS:
    urlpatterns.append(url(r'^tinymce/', include('tinymce.urls')))

if 'newsletter' in settings.INSTALLED_APPS:
    urlpatterns.append(url(r'^newsletter/', include('newsletter.urls')))

if 'django_select2' in settings.INSTALLED_APPS:
    urlpatterns.append(url(r'^select2/', include('django_select2.urls')))

if 'django_uwsgi' in settings.INSTALLED_APPS:
    urlpatterns.insert(0, url(r'^admin/uwsgi/', include('django_uwsgi.urls')))