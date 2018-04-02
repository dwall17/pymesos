# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# See include/mesos/scheduler.hpp, include/mesos/executor.hpp and
# include/mesos/mesos.proto for more information documenting this
# interface.

"""Python bindings for Mesos."""

from __future__ import print_function

import sys

__all__ = (
  'Executor',
  'ExecutorDriver',
  'Scheduler',
  'SchedulerDriver',
  'OperatorMasterDriver'
  'OperatorMaster',
  'OperatorAgentDriver',
)

class Scheduler(object):
  """
    Base class for Mesos schedulers. Users' schedulers should extend this
    class to get default implementations of methods they don't override.
  """

  def registered(self, driver, frameworkId, masterInfo):
    """
      Invoked when the scheduler successfully registers with a Mesos master.
      It is called with the frameworkId, a unique ID generated by the
      master, and the masterInfo which is information about the master
      itself.
    """

  def reregistered(self, driver, masterInfo):
    """
      Invoked when the scheduler re-registers with a newly elected Mesos
      master.  This is only called when the scheduler has previously been
      registered.  masterInfo contains information about the newly elected
      master.
    """

  def disconnected(self, driver):
    """
      Invoked when the scheduler becomes disconnected from the master, e.g.
      the master fails and another is taking over.
    """

  def processHeartBeat(self):
    """
      Invoked when the scheduler gets a heartbeat
    """

  def resourceOffers(self, driver, offers):
    """
      Invoked when resources have been offered to this framework. A single
      offer will only contain resources from a single slave.  Resources
      associated with an offer will not be re-offered to _this_ framework
      until either (a) this framework has rejected those resources (see
      SchedulerDriver.launchTasks) or (b) those resources have been
      rescinded (see Scheduler.offerRescinded).  Note that resources may be
      concurrently offered to more than one framework at a time (depending
      on the allocator being used).  In that case, the first framework to
      launch tasks using those resources will be able to use them while the
      other frameworks will have those resources rescinded (or if a
      framework has already launched tasks with those resources then those
      tasks will fail with a TASK_LOST status and a message saying as much).
    """

  def inverseOffers(self, driver, offers):
    """
      Invoked when an inverse offer is sent to the framework.  An inverse
      offer and a resource offer can hold many of the same fields, but an
      inverse offer requests resources rather than offering them.  Inverse
      offers may be accepted, rejected, re-offered, and rescinded.
    """

  def offerRescinded(self, driver, offerId):
    """
      Invoked when an offer is no longer valid (e.g., the slave was lost or
      another framework used resources in the offer.) If for whatever reason
      an offer is never rescinded (e.g., dropped message, failing over
      framework, etc.), a framework that attempts to launch tasks using an
      invalid offer will receive TASK_LOST status updates for those tasks
      (see Scheduler.resourceOffers).
    """

  def inverseOfferRescinded(self, driver, offerId):
    """
      Invoked when an inverse offer is no longer valid (e.g., the slave was lost or
      another framework used resources in the inverse offer.) If for whatever reason
      an inverse offer is never rescinded (e.g., dropped message, failing over
      framework, etc.), a framework that attempts to launch tasks using an
      invalid inverse offer will receive TASK_LOST status updates for those tasks
      (see Scheduler.resourceOffers).
    """

  def statusUpdate(self, driver, status):
    """
      Invoked when the status of a task has changed (e.g., a slave is
      lost and so the task is lost, a task finishes and an executor
      sends a status update saying so, etc). If implicit
      acknowledgements are being used, then returning from this
      callback _acknowledges_ receipt of this status update! If for
      whatever reason the scheduler aborts during this callback (or
      the process exits) another status update will be delivered (note,
      however, that this is currently not true if the slave sending the
      status update is lost/fails during that time). If explicit
      acknowledgements are in use, the scheduler must acknowledge this
      status on the driver.
    """

  def operationStatusUpdate(self, driver, status):
    """
      Invoked when there is an operation status update generated by the
      master, agent, or resource provider. These updates are only sent to
      the framework for operations which had the operation ID set by the
      framework. It is the responsibility of the scheduler to explicitly
      acknowledge the receipt of a status update.
    """

  def frameworkMessage(self, driver, executorId, slaveId, message):
    """
      Invoked when an executor sends a message. These messages are best
      effort; do not expect a framework message to be retransmitted in any
      reliable fashion.
    """

  def slaveLost(self, driver, slaveId):
    """
      Invoked when a slave has been determined unreachable (e.g., machine
      failure, network partition.) Most frameworks will need to reschedule
      any tasks launched on this slave on a new slave.

      NOTE: This callback is not reliably delivered. If a host or
      network failure causes messages between the master and the
      scheduler to be dropped, this callback may not be invoked.
    """

  def executorLost(self, driver, executorId, slaveId, status):
    """
      Invoked when an executor has exited/terminated. Note that any tasks
      running will have TASK_LOST status updates automatically generated.

      NOTE: This callback is not reliably delivered. If a host or
      network failure causes messages between the master and the
      scheduler to be dropped, this callback may not be invoked.
    """

  def error(self, driver, message):
    """
      Invoked when there is an unrecoverable error in the scheduler or
      scheduler driver.  The driver will be aborted BEFORE invoking this
      callback.
    """
    print("Error from Mesos: %s " % message, file=sys.stderr)


class SchedulerDriver(object):
  """
    Interface for Mesos scheduler drivers. Users may wish to implement this
    class in mock objects for tests.
  """
  def start(self):
    """
      Starts the scheduler driver.  This needs to be called before any other
      driver calls are made.
    """

  def stop(self, failover=False):
    """
      Stops the scheduler driver. If the 'failover' flag is set to False
      then it is expected that this framework will never reconnect to Mesos
      and all of its executors and tasks can be terminated.  Otherwise, all
      executors and tasks will remain running (for some framework specific
      failover timeout) allowing the scheduler to reconnect (possibly in the
      same process, or from a different process, for example, on a different
      machine.)
    """

  def abort(self):
    """
      Aborts the driver so that no more callbacks can be made to the
      scheduler.  The semantics of abort and stop have deliberately been
      separated so that code can detect an aborted driver (i.e., via the
      return status of SchedulerDriver.join), and instantiate and start
      another driver if desired (from within the same process.)
    """

  def join(self):
    """
      Waits for the driver to be stopped or aborted, possibly blocking the
      current thread indefinitely.  The return status of this function can
      be used to determine if the driver was aborted (see mesos.proto for a
      description of Status).
    """

  def run(self):
    """
      Starts and immediately joins (i.e., blocks on) the driver.
    """

  def requestResources(self, requests):
    """
      Requests resources from Mesos (see mesos.proto for a description of
      Request and how, for example, to request resources from specific
      slaves.)  Any resources available are offered to the framework via
      Scheduler.resourceOffers callback, asynchronously.
    """

  def launchTasks(self, offerIds, tasks, filters=None):
    """
      Launches the given set of tasks. Any remaining resources (i.e.,
      those that are not used by the launched tasks or their executors)
      will be considered declined. Note that this includes resources
      used by tasks that the framework attempted to launch but failed
      (with TASK_ERROR) due to a malformed task description. The
      specified filters are applied on all unused resources (see
      mesos.proto for a description of Filters). Available resources
      are aggregated when multiple offers are provided. Note that all
      offers must belong to the same slave. Invoking this function with
      an empty collection of tasks declines offers in their entirety
      (see Scheduler.declineOffer). Note that passing a single offer
      is also supported.
    """

  def killTask(self, taskId):
    """
      Kills the specified task. Note that attempting to kill a task is
      currently not reliable.  If, for example, a scheduler fails over while
      it was attempting to kill a task it will need to retry in the future.
      Likewise, if unregistered / disconnected, the request will be dropped
      dropped (these semantics may be changed in the future).
    """

  def acceptOffers(self, offerIds, operations, filters=None):
    """
      Accepts the given offers and performs a sequence of operations on
      those accepted offers. See Offer.Operation in mesos.proto for the
      set of available operations. Any remaining resources (i.e., those
      that are not used by the launched tasks or their executors) will
      be considered declined. Note that this includes resources used by
      tasks that the framework attempted to launch but failed (with
      TASK_ERROR) due to a malformed task description. The specified
      filters are applied on all unused resources (see mesos.proto for
      a description of Filters). Available resources are aggregated
      when multiple offers are provided. Note that all offers must
      belong to the same slave.
    """

  def acceptInverseOffers(self, offer_ids, filters=None):
    """
      Accepts an inverse offer. Inverse offers should only be accepted
      if the resources in the offer can be safely evacuated before the
      provided unavailability.
    """

  def declineOffer(self, offerId, filters=None):
    """
      Declines an offer in its entirety and applies the specified
      filters on the resources (see mesos.proto for a description of
      Filters). Note that this can be done at any time, it is not
      necessary to do this within the Scheduler::resourceOffers
      callback.
    """

  def declineInverseOffer(self, offer_ids, filters=None):
    """
      Declines an inverse offer. Inverse offers should be declined if
      the resources in the offer might not be safely evacuated before
      the provided unavailability.
    """

  def reviveOffers(self):
    """
      Removes all filters previously set by the framework (via
      launchTasks()).  This enables the framework to receive offers from
      those filtered slaves.
    """

  def suppressOffers(self):
    """
      Inform Mesos master to stop sending offers to the framework. The
      scheduler should call reviveOffers() to resume getting offers.
    """

  def acknowledgeStatusUpdate(self, status):
    """
      Acknowledges the status update. This should only be called
      once the status update is processed durably by the scheduler.
      Not that explicit acknowledgements must be requested via the
      constructor argument, otherwise a call to this method will
      cause the driver to crash.
    """

  def acknowledgeOperationStatusUpdate(self, status):
    """
      Acknowledges the operation status update. This should only be called
      once the operation status update is processed durably by the scheduler.
      Not that explicit acknowledgements must be requested via the
      constructor argument, otherwise a call to this method will
      cause the driver to crash.
    """

  def sendFrameworkMessage(self, executorId, slaveId, data):
    """
      Sends a message from the framework to one of its executors. These
      messages are best effort; do not expect a framework message to be
      retransmitted in any reliable fashion.
    """

  def reconcileTasks(self, tasks):
    """
      Allows the framework to query the status for non-terminal tasks.
      This causes the master to send back the latest task status for
      each task in 'statuses', if possible. Tasks that are no longer
      known will result in a TASK_LOST update. If statuses is empty,
      then the master will send the latest status for each task
      currently known.
    """

class Executor(object):
  """
    Base class for Mesos executors. Users' executors should extend this
    class to get default implementations of methods they don't override.
  """

  def registered(self, driver, executorInfo, frameworkInfo, slaveInfo):
    """
      Invoked once the executor driver has been able to successfully connect
      with Mesos.  In particular, a scheduler can pass some data to its
      executors through the FrameworkInfo.ExecutorInfo's data field.
    """

  def reregistered(self, driver, slaveInfo):
    """
      Invoked when the executor re-registers with a restarted slave.
    """

  def disconnected(self, driver):
    """
      Invoked when the executor becomes "disconnected" from the slave (e.g.,
      the slave is being restarted due to an upgrade).
    """

  def launchTask(self, driver, task):
    """
      Invoked when a task has been launched on this executor (initiated via
      Scheduler.launchTasks).  Note that this task can be realized with a
      thread, a process, or some simple computation, however, no other
      callbacks will be invoked on this executor until this callback has
      returned.
    """

  def launchTaskGroup(self, driver, task_infos):
    """
      Invoked when a task group has been launched on this executor (initiated via
      Scheduler.launchTasks).  Note that this task can be realized with a
      thread, a process, or some simple computation, however, no other
      callbacks will be invoked on this executor until this callback has
      returned.
    """

  def killTask(self, driver, taskId):
    """
      Invoked when a task running within this executor has been killed (via
      SchedulerDriver.killTask).  Note that no status update will be sent on
      behalf of the executor, the executor is responsible for creating a new
      TaskStatus (i.e., with TASK_KILLED) and invoking ExecutorDriver's
      sendStatusUpdate.
    """

  def frameworkMessage(self, driver, message):
    """
      Invoked when a framework message has arrived for this executor.  These
      messages are best effort; do not expect a framework message to be
      retransmitted in any reliable fashion.
    """

  def shutdown(self, driver):
    """
      Invoked when the executor should terminate all of its currently
      running tasks.  Note that after Mesos has determined that an executor
      has terminated any tasks that the executor did not send terminal
      status updates for (e.g., TASK_KILLED, TASK_FINISHED, TASK_FAILED,
      etc) a TASK_LOST status update will be created.
    """

  def error(self, driver, message):
    """
      Invoked when a fatal error has occurred with the executor and/or
      executor driver.  The driver will be aborted BEFORE invoking this
      callback.
    """
    print("Error from Mesos: %s" % message, file=sys.stderr)



class ExecutorDriver(object):
  """
    Interface for Mesos executor drivers. Users may wish to extend this
    class in mock objects for tests.
  """
  def start(self):
    """
      Starts the executor driver. This needs to be called before any other
      driver calls are made.
    """

  def stop(self):
    """
      Stops the executor driver.
    """

  def abort(self):
    """
      Aborts the driver so that no more callbacks can be made to the
      executor.  The semantics of abort and stop have deliberately been
      separated so that code can detect an aborted driver (i.e., via the
      return status of ExecutorDriver.join), and instantiate and start
      another driver if desired (from within the same process, although this
      functionality is currently not supported for executors).
    """

  def join(self):
    """
      Waits for the driver to be stopped or aborted, possibly blocking the
      current thread indefinitely.  The return status of this function can
      be used to determine if the driver was aborted (see mesos.proto for a
      description of Status).
    """

  def run(self):
    """
      Starts and immediately joins (i.e., blocks on) the driver.
    """

  def sendStatusUpdate(self, status):
    """
      Sends a status update to the framework scheduler, retrying as
      necessary until an acknowledgement has been received or the executor
      is terminated (in which case, a TASK_LOST status update will be sent).
      See Scheduler.statusUpdate for more information about status update
      acknowledgements.
    """

  def sendFrameworkMessage(self, data):
    """
      Sends a message to the framework scheduler. These messages are best
      effort; do not expect a framework message to be retransmitted in any
      reliable fashion.
    """


class OperatorDaemonDriver(object):
  """
    Operator HTTP API: Operations common to master daemon and agent daemon.
  """

  def getHealth(self):
    """
      This call retrieves the health status of master daemon or agent daemon.
    """

  def getFlags(self):
    """
      This call retrieves the daemon's overall flag configuration.
    """

  def getVersion(self):
    """
      This call retrieves the daemon's version information.
    """

  def getMetrics(self, timeout):
    """
      This call gives the snapshot of current metrics to the end user. If timeout is set in the call, it would be used
      to determine the maximum amount of time the API will take to respond. If the timeout is exceeded, some metrics may
      not be included in the response.
    """

  def getLoggingLevel(self):
    """
      This call retrieves the daemon's logging level.
    """

  def setLoggingLevel(self, level, duration):
    """
      Sets the logging verbosity level for a specified duration for master daemon or agent daemon. Mesos uses glog for
      logging. The library only uses verbose logging which means nothing will be output unless the verbosity level is
      set (by default it's 0, libprocess uses levels 1, 2, and 3).
    """

  def listFiles(self, path):
    """
      This call retrieves the file listing for a directory in master daemon or agent daemon.
    """

  def readFile(self, path, offset, length):
    """
      Reads data from a file. This call takes path of the file to be read in the daemon, offset to start reading
      position and length for the maximum number of bytes to read.
    """

  def getState(self):
    """
      This call retrieves the overall cluster state.
    """

  def getFrameworks(self):
    """
      This call retrieves information about all the frameworks known to the master daemon or agent daemon.
    """

  def getExecutors(self):
    """
      Queries about all the executors known to the master daemon or agent daemon.
    """

  def getTasks(self):
    """
      Query about all the tasks known to the master daemon or agent daemon.
    """


class OperatorMasterDriver(OperatorDaemonDriver):
  """
    Interface for Mesos operator drivers. Users may wish to extend this
    class in mock objects for tests.
  """

  def start(self):
    """
      Starts the operator driver. This needs to be called before any other
      driver calls are made.
    """

  def stop(self):
    """
      Stops the operator driver.
    """

  def abort(self):
    """
      Aborts the driver so that no more callbacks can be made to the
      operator.  The semantics of abort and stop have deliberately been
      separated so that code can detect an aborted driver (i.e., via the
      return status of OperatorMasterDriver.join), and instantiate and start
      another driver if desired (from within the same process, although this
      functionality is currently not supported for executors).
    """

  def join(self):
    """
      Waits for the driver to be stopped or aborted, possibly blocking the
      current thread indefinitely.  The return status of this function can
      be used to determine if the driver was aborted (see mesos.proto for a
      description of Status).
    """

  def run(self):
    """
      Starts and immediately joins (i.e., blocks on) the driver.
    """

  def getAgents(self):
    """
      This call retrieves information about all the agents known to the master.
    """

  def getRoles(self):
    """
      Query the information about roles.
    """

  def getWeights(self):
    """
      This call retrieves the information about role weights.
    """

  def updateWeights(self, weight_infos):
    """
      This call updates weights for specific role. This call takes weight_infos which needs role value and weight value.
    """

  def getMaster(self):
    """
      This call retrieves the information on master.
    """

  def reserveResources(self, agent_id, resources):
    """
      This call reserve resources dynamically on a specific agent. This call takes agent_id and resources details like
      the following.
    """

  def unreserveResources(self, agent_id, resources):
    """
      This call unreserve resources dynamically on a specific agent. This call takes agent_id and resources details like
      the following.
    """

  def createVolumes(self, agent_id, volumes):
    """
      This call create persistent volumes on reserved resources. The request is forwarded asynchronously to the Mesos
      agent where the reserved resources are located. That asynchronous message may not be delivered or creating the
      volumes at the agent might fail. This call takes agent_id and volumes details like the following.
    """

  def destroyVolumes(self, agent_id, volumes):
    """
      This call destroys persistent volumes. The request is forwarded asynchronously to the Mesos agent where the
      reserved resources are located.
    """

  def getMaintenanceStatus(self):
    """
      This call retrieves the cluster's maintenance status.
    """

  def getMaintenanceSchedule(self):
    """
      This call retrieves the cluster's maintenance status.
    """

  def updateMaintenanceSchedule(self, windows):
    """
      This call retrieves the cluster's maintenance schedule.
    """

  def startMaintenance(self, machines):
    """
      This call starts the maintenance of the cluster, this would bring a set of machines down.
    """

  def stopMaintenance(self, machines):
    """
      Stops the maintenance of the cluster, this would bring a set of machines back up.
    """

  def getQuota(self):
    """
      This call retrieves the cluster's configured quotas.
    """

  def setQuota(self, quota_request):
    """
      This call sets the quota for resources to be used by a particular role.
    """

  def removeQuota(self, role):
    """
      This call removes the quota for a particular role.
    """

  def markAgentGone(self, agent_id):
    """
      This call can be used by operators to assert that an agent instance has failed and is never coming back
      (e.g., ephemeral instance from cloud provider). The master would shutdown the agent and send TASK_GONE_BY_OPERATOR
      updates for all the running tasks. This signal can be used by stateful frameworks to re-schedule their workloads
      (volumes, reservations etc.) to other agent instances. It is possible that the tasks might still be running if the
      operator's assertion was wrong and the agent was partitioned away from the master. The agent would be shutdown
      when it tries to re-register with the master when the partition heals. This call is idempotent.
    """

class OperatorMaster(object):
  """
    Base class for Mesos operators. Users' operators should extend this
    class to get default implementations of methods they don't override.
  """

  # def heartbeat(self):
  #   """
  #     Periodically sent by the master to the subscriber according to 'Subscribed.heartbeat_interval_seconds'. If the
  #     subscriber does not receive any events (including heartbeats) for an extended period of time (e.g., 5 x
  #     heartbeat_interval_seconds), it is likely that the connection is lost or there is a network partition. In that
  #     case, the subscriber should close the existing subscription connection and resubscribe using a backoff strategy.
  #   """

  def taskAdded(self, task_info):
    """
      Invoked whenever a task has been added to the master. This can happen either when a new task launch is processed
      by the master or when an agent re-registers with a failed over master.
    """

  def taskUpdated(self, task_info):
    """
      Invoked whenever the state of the task changes in the master. This can happen when a status update is received or
      generated by the master. Since status updates are retried by the agent, not all status updates received by the
      master result in the event being sent.
    """

  def frameworkAdded(self, framework_info):
    """
      Sent whenever a framework becomes known to the master. This can happen when a new framework registers with the
      master.
    """

  def frameworkUpdated(self, framework_info):
    """
      Sent whenever a framework re-registers with the master upon a disconnection (network error) or upon a master
      failover.
    """

  def frameworkRemoved(self, framework_info):
    """
      Sent whenever a framework is removed. This can happen when a framework is explicitly teardown by the operator or
      if it fails to re-register with the master within the failover timeout.
    """

  def agentAdded(self, agent_info):
    """
      Sent whenever an agent becomes known to it. This can happen when an agent registered for the first time, or
      reregistered after a master failover.
    """

  def agentRemoved(self, agent_id):
    """
      Sent whenever a agent is removed. This can happen when the agent is scheduled for maintenance. (NOTE: It's
      possible that an agent might become active once it has been removed, i.e. if the master has gc'ed its list of
      known "dead" agents. See MESOS-5965 for context).
    """

class OperatorAgentDriver(OperatorDaemonDriver):
  """
    This API contains all the calls accepted by the agent.
  """

  def getContainers(self):
    """
      This call retrieves information about containers running on this agent. It contains ContainerStatus and
      ResourceStatistics along with some metadata of the containers.
    """

  def launchNestedContainer(self, launch_nested_container):
    """
      This call launches a nested container. Any authorized entity, including the executor itself, its tasks, or the
      operator can use this API to launch a nested container.
    """

  def waitNestedContainer(self, container_id, parent_id=None):
    """
      This call waits for a nested container to terminate or exit. Any authorized entity, including the executor itself,
      its tasks, or the operator can use this API to wait on a nested container.
    """

  def killNestedContainer(self, container_id, parent_id=None):
    """
      This call initiates the destruction of a nested container. Any authorized entity, including the executor itself,
      its tasks, or the operator can use this API to kill a nested container.
    """

  def launchNestedContainerSession(self, launch_nested_container_session):
    """
      This call launches a nested container whose lifetime is tied to the lifetime of the HTTP call establishing this
      connection. The STDOUT and STDERR of the nested container is streamed back to the client so long as the connection
      is active.
    """

  def attachContainerInput(self, container_id):
    """
      This call attaches to the STDIN of the primary process of a container and streams input to it. This call can only
      be made against containers that have been launched with an associated IOSwitchboard (i.e. nested containers
      launched via a LAUNCH_NESTED_CONTAINER_SESSION call or normal containers launched with a TTYInfo in their
      ContainerInfo). Only one ATTACH_CONTAINER_INPUT call can be active for a given container at a time. Subsequent
      attempts to attach will fail.

      The first message sent over an ATTACH_CONTAINER_INPUT stream must be of type CONTAINER_ID and contain the
      ContainerID of the container being attached to. Subsequent messages must be of type PROCESS_IO, but they may
      contain subtypes of either DATA or CONTROL. DATA messages must be of type STDIN and contain the actual data to
      stream to the STDIN of the container being attached to. Currently, the only valid CONTROL message sends a
      heartbeat to keep the connection alive. We may add more CONTROL messages in the future.
    """

  def attachContainerOutput(self, container_id):
    """
      This call attaches to the STDOUT and STDERR of the primary process of a container and streams its output back to
      the client. This call can only be made against containers that have been launched with an associated IOSwitchboard
      (i.e. nested containers launched via a LAUNCH_NESTED_CONTAINER_SESSION call or normal containers launched with a
      TTYInfo in their ContainerInfo field). Multiple ATTACH_CONTAINER_OUTPUT calls can be active for a given container
      at once.
    """

  def removeNestedContainer(self, container_id, parent_id = None):
    """
      This call triggers the removal of a nested container and its artifacts (e.g., the sandbox and runtime directories).
      This call can only be made against containers that have already terminated, and whose parent container has not
      been destroyed. Any authorized entity, including the executor itself, its tasks, or the operator can use this API
      call.
    """

  def addResourceProviderConfig(self, info):
    """
      This call launches a Local Resource Provider on the agent with the specified ResourceProviderInfo.
    """

  def updateResourceProviderConfig(self, info):
    """
      This call updates a Local Resource Provider on the agent with the specified ResourceProviderInfo.
    """

  def removeResourceProviderConfig(self, type, name):
    """
      This call terminates a given Local Resource Provider on the agent and prevents it from being launched again until
      the config is added back. The master and the agent will think the resource provider has disconnected, similar to
      agent disconnection.
      If there exists a task that is using the resources provided by the resource provider, its execution will not be
      affected. However, offer operations for the local resource provider will not be successful. In fact, if a local
      resource provider is disconnected, the master will rescind the offers related to that local resource provider,
      effectively disallowing frameworks to perform operations on the disconnected local resource provider.
      The local resource provider can be re-added after its removal using ADD_RESOURCE_PROVIDER_CONFIG. Note that
      removing a local resource provider is different than marking a local resource provider as gone, in which case the
      local resource provider will not be allowed to be re-added. Marking a local resource provider as gone is not yet
      supported.
    """

  def pruneImages(self, excluded_images=None):
    """
      This call triggers garbage collection for container images. This call can only be made when all running containers
      are launched with Mesos version 1.5 or newer. An optional list of excluded images from GC can be speficied via
      prune_images.excluded_images field.
    """
