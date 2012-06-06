# -*- encoding: utf-8 -*-
import datetime

from django.views import generic as generic_views
from django.views.generic.base import TemplateResponseMixin
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from . import models, forms, utils


class ListProposalsView(generic_views.TemplateView):
    """
    Lists all proposals the reviewer should be able to review, sorted by
    "priority".

    This listing should include some filter functionality to filter proposals
    by tag, track or kind.

    Access: review-team
    """
    template_name = 'reviews/reviewable_proposals.html'
    order_mapping = {
        'comments': 'review_metadata__num_comments',
        'reviews': 'review_metadata__num_reviews',
        'title': 'title',
        'activity': 'review_metadata__latest_activity_date',
    }

    def get_context_data(self, **kwargs):
        if not utils.can_review_proposal(self.request.user, None):
            return HttpResponseForbidden()
        proposals = models.Proposal.objects.select_related('review_metadata').order_by(self.get_order()).all()
        my_reviews = models.Review.objects.filter(user=self.request.user).select_related('proposal')
        reviewed_proposals = [rev.proposal for rev in my_reviews]
        for proposal in proposals:
            proposal.reviewed = proposal in reviewed_proposals
        return {
            'proposals': proposals
        }

    def get_order(self):
        order = self.request.GET.get('order', 'reviews')
        dir_ = ''
        if order.startswith('-'):
            dir_ = '-'
            order = order[1:]
        order = self.order_mapping.get(order, 'review_metadata__num_reviews')
        return '{0}{1}'.format(dir_, order)


class SubmitReviewView(generic_views.TemplateView):
    """
    Only reviewers should be able to submit reviews as long as the proposal
    accepts one. The review-period should perhaps coincide with closing
    the proposal for discussion.

    Access: review-team
    """
    # TODO: Freeze the proposal version from GET -> POST
    template_name = 'reviews/submit_review_form.html'
    form = None

    def post(self, request, *args, **kwargs):
        self.form = forms.ReviewForm(data=request.POST)
        if self.form.is_valid():
            review = self.form.save(commit=False)
            review.proposal = self.proposal
            review.proposal_version = self.proposal_version
            review.user = request.user
            review.save()
            messages.success(request, "Bewertung gespeichert")
            return HttpResponseRedirect(reverse('reviews-proposal-details', kwargs={'pk': self.proposal.pk}))
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        if self.form is None:
            self.form = forms.ReviewForm()
        return {
            'form': self.form
        }

    def dispatch(self, request, *args, **kwargs):
        self.proposal = get_object_or_404(models.Proposal, pk=kwargs['pk'])
        if models.Review.objects.filter(user=request.user, proposal=self.proposal).count():
            messages.info(request, "Sie haben diesen Vorschlag bereits bewertet")
            return HttpResponseRedirect(reverse('reviews-proposal-details', kwargs={'pk': self.proposal.pk}))
        if not utils.can_review_proposal(request.user, self.proposal):
            return HttpResponseForbidden()
        self.proposal_version = models.ProposalVersion.objects.get_latest_for(self.proposal)
        return super(SubmitReviewView, self).dispatch(request, *args, **kwargs)


class UpdateReviewView(generic_views.UpdateView):
    model = models.Review
    template_name_suffix = '_update_form'
    form_class = forms.UpdateReviewForm

    def get_object(self):
        return self.model.objects.get(user=self.request.user, proposal__pk=self.kwargs['pk'])

    def form_valid(self, form):
        messages.success(self.request, u"Änderungen gespeichert")
        return super(UpdateReviewView, self).form_valid(form)

    def get_success_url(self):
        return reverse('reviews-proposal-details', kwargs={'pk': self.kwargs['pk']})


class DeleteReviewView(generic_views.DeleteView):
    model = models.Review

    def get_object(self):
        return self.model.objects.get(user=self.request.user, proposal__pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse('reviews-proposal-details', kwargs={'pk': self.kwargs['pk']})


class SubmitCommentView(TemplateResponseMixin, generic_views.View):
    """
    Everyone on the review-team as well as the original author should be
    able to comment on a proposal.

    Access: speaker, co-speakers and review-team
    """
    template_name = 'reviews/comment_form.html'

    def get(self, request, *args, **kwargs):
        if not hasattr(self, 'form') or self.form is None:
            self.form = forms.CommentForm()
        return self.render_to_response({
            'form': self.form
            })

    def post(self, request, *args, **kwargs):
        self.form = forms.CommentForm(data=request.POST)
        if self.form.is_valid():
            comment = self.form.save(commit=False)
            comment.author = request.user
            comment.proposal = self.proposal
            comment.proposal_version = self.proposal_version
            comment.save()
            messages.success(request, _("Comment added"))
            # TODO: Send notification mails
            return HttpResponseRedirect(reverse('reviews-proposal-details', kwargs={'pk': self.proposal.pk}))
        return self.get(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        self.proposal = get_object_or_404(models.Proposal, pk=kwargs['pk'])
        if not utils.can_participate_in_review(request.user, self.proposal):
            return HttpResponseForbidden()
        self.proposal_version = models.ProposalVersion.objects.get_latest_for(self.proposal)
        return super(SubmitCommentView, self).dispatch(request, *args, **kwargs)


class ProposalDetailsView(generic_views.DetailView):
    """
    An extended version of the details view of the proposals app that
    also includes the discussion as well as the review of the current user.

    Access: author and review-team
    Template: reviews/proposal_details.html
    """
    model = models.Proposal

    def get_template_names(self):
        return ['reviews/proposal_details.html']

    def get_context_data(self, **kwargs):
        comment_form = forms.CommentForm()
        comment_form.helper.form_action = reverse('reviews-submit-comment', kwargs={'pk': self.object.pk})
        comments = self.object.comments.all()
        proposal_versions = self.object.versions.all()
        data = super(ProposalDetailsView, self).get_context_data(**kwargs)
        data['comments'] = comments
        data['proposal_version'] = models.ProposalVersion.objects.get_latest_for(self.object)
        data['comment_form'] = comment_form
        data['versions'] = proposal_versions
        data['timeline'] = map(self.wrap_timeline_elements, utils.merge_comments_and_versions(comments, proposal_versions))
        data['can_review'] = utils.can_review_proposal(self.request.user, self.object)
        try:
            data['user_review'] = self.object.reviews.filter(user=self.request.user)[0]
        except:
            pass
        return data

    def get_object(self, queryset=None):
        proposal = super(ProposalDetailsView, self).get_object(queryset)
        if utils.can_participate_in_review(self.request.user, proposal):
            return proposal
        return HttpResponseForbidden()

    def wrap_timeline_elements(self, item):
        type_ = 'comment'
        if isinstance(item, models.ProposalVersion):
            type_ = 'version'
        return {
            'type': type_,
            'item': item
        }


class UpdateProposalView(TemplateResponseMixin, generic_views.View):
    """
    This should create a new version of the proposal and notify all
    contributors to the discussion so far.

    Access: speaker and co-speakers
    """
    template_name = 'reviews/update_proposal.html'
    form = None

    def get(self, request, *args, **kwargs):
        if self.form is None:
            if self.proposal_version:
                self.form = forms.UpdateProposalForm.init_from_proposal(self.proposal_version)
            else:
                self.form = forms.UpdateProposalForm.init_from_proposal(self.object)
        return self.render_to_response({
            'form': self.form,
            'proposal': self.object,
            'proposal_version': self.proposal_version
            })

    def post(self, request, *args, **kwargs):
        self.form = forms.UpdateProposalForm(data=request.POST)
        if not self.form.is_valid():
            return self.get(request, *args, **kwargs)
        new_version = models.ProposalVersion(
            title=self.form.cleaned_data['title'],
            description=self.form.cleaned_data['description'],
            abstract=self.form.cleaned_data['abstract'],
            pub_date=datetime.datetime.now(),
            original=self.object,
            creator=request.user
            )
        new_version.save()
        messages.success(request, _("Proposal successfully update"))
        # TODO: Send notification mails
        return HttpResponseRedirect(reverse('reviews-proposal-details', kwargs={'pk': self.object.pk}))

    def dispatch(self, request, *args, **kwargs):
        self.object = get_object_or_404(models.Proposal.objects, pk=kwargs['pk'])
        self.proposal_version = models.ProposalVersion.objects.get_latest_for(self.object)
        if not utils.is_proposal_author(request.user, self.object):
            return HttpResponseForbidden()
        return super(UpdateProposalView, self).dispatch(request, *args, **kwargs)


class ReviewOverviewView(object):
    """
    This view should provide the organisers with an overview of the review
    progress and should indicate how many proposals have been reviewed so far
    and their current scores.

    Access: staff
    """
    pass


class OpenProposalForReviewsView(object):
    """
    The moment a proposal is opened for reviews, a ProposalVersion is created
    in order to act as a snapshot on which the reviewers can rely on.

    Access: staff
    """
    pass
