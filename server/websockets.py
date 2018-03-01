# Receive and send websockets messages.
# Clients open a socket on a specific workflow, and all clients viewing that workflow are a "group"
from server.models import Workflow
from server.models.WfModule import ws_callbacks
from channels.consumer import SyncConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json


# Convert workflow id to channel group name
def workflow_ws_group(id):
    return "workflow-" + str(id)


# Channels creates one of these handler objects for each ws connection
# Can't use WebsocketConsumer here because our group depends on the url, determined only at connect
class WebsocketsHandler(SyncConsumer):

    # Clients connect to channels at ws://server/workflows/[id]
    # This extracts the id. Throws ValueError if id is not an int
    def _id(self):
        id = self.scope['path'].rstrip('/').split('/')[-1]
        return int(id)


    # Client connects to URL to start monitoring for changes
    def websocket_connect(self, event):
        id = self._id()
        try:
            Workflow.objects.get(pk=id)
        except Workflow.DoesNotExist:
            self.send({"type": "websocket.close"})  # can't find that workflow, don't connect
            return

        self.send({ "type": "websocket.accept"})
        async_to_sync(self.channel_layer.group_add(workflow_ws_group(id), self.channel_name))


    # Remove from workflow group when client disconnects
    def websocket_disconnect(self, event):
        async_to_sync(self.channel_layer.group_discard(workflow_ws_group(self._id()), self.channel_name))


    # we do not expect clients to tell us things on over this channel
    def websocket_receive(self, event):
        pass


channel_layer = get_channel_layer()


# --- Public API ---

# Send a message to all clients listening to a workflow
def ws_send_workflow_update(workflow, message_dict):
    # print("Sending message to " + str(workflow.id) + ": " + str(message_dict))
    group = workflow_ws_group(workflow.id)
    payload = {'text' : json.dumps(message_dict)}
    async_to_sync(channel_layer.group_send(group, payload))

# Tell clients to reload entire workflow
def ws_client_rerender_workflow(workflow):
    message = { 'type': 'reload-workflow'}
    ws_send_workflow_update(workflow, message)

# Tell clients to reload specific wfmodule
def ws_client_wf_module_status(wf_module, status):
    workflow = wf_module.workflow
    if workflow is not None:
        message = { 'type' : 'wfmodule-status', 'id' : wf_module.id, 'status' : status}
        ws_send_workflow_update(workflow, message)

# Completely ridiculous work to resolve circular imports: websockets -> Workflow -> WfModule which needs websockets
# So we create an object with callbacks in WfModule, which we then fill out here
ws_callbacks.ws_client_rerender_workflow = ws_client_rerender_workflow
ws_callbacks.ws_client_wf_module_status = ws_client_wf_module_status