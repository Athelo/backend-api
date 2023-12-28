import logging
from http.client import BAD_REQUEST, CREATED, UNPROCESSABLE_ENTITY

from api.utils import class_route
from flask import Blueprint
from flask.views import MethodView

logger = logging.getLogger()

common_endpoints = Blueprint("Common", __name__, url_prefix="/api/v1/common")


@class_route(common_endpoints, "/enums", "enums")
class EnumsView(MethodView):
    def get(self):
        return {
            "third_party_access_token_source":[["facebook","Facebook"],["google-oauth2","Google"],["apple-id","Apple"]],"friend_request_status":[[1,"Pending"],[2,"Accepted"],[3,"Rejected"]],"userprofile_status":[[1,"Friend"],[2,"Invitation received"],[3,"We rejected their invite"],[4,"Invitation sent"],[5,"Not connected"]],"inappropriate_content_reason":[[1,"Bad language"],[2,"Other"]],"user_profile_check_list_item_status":[[1,"Not started"],[2,"In progress"],[3,"Complete"],[4,"Cancelled"]],"reported_chat_message_type":[[1,"Regular"],[2,"Mass public"],[3,"Mass private"]],"feedback_category":[[1,"General"],[2,"Other"],[3,"Question"],[4,"Report an issue"]],"chat_room_type":[[1,"Regular"],[2,"Mass public"],[3,"Mass private"]],"sleep_level":[["wake","Wake"],["light","Light"],["deep","Deep"],["rem","Rem"],["unknown","Unknown"]],"caregiving_permission_level":[["No access","NO_ACCESS"],["Access","ACCESS"]],"caregiver_relation_label":[["friend","Friend"],["relative","Relative"],["familiar_person","Familiar person"]],"caregiver_invitation_status":[["processing","Processing"],["sent","Sent"],["consumed","Consumed"],["timeout","Timeout"],["canceled","Canceled"]],"athelo_user_type":[[1,"Remission"],[2,"Active treatment"],[3,"Caregiver / Support Network"]]
        }