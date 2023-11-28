## Why do we use websockets?

Because we need access to Mephisto data model, like agent, worker etc.
Web sockets are the only method for live communication Mephisto provides.

Alternatives:

* Implement API endpoints with separate web server and query Mephisto db directly.
  This would mean that we would need to re-implement a lot of Mephisto. Further,
  Mephisto is in an early state and db could change. Not to mention that Mephisto
  might implement other database backends. Also, we would need to authenticate
  the frontend to our second web server.
* Just use a static dashboard

Caveats:

* Mephisto creates web sockets only during running units/assignments. This means
  that we can't create a dashboard on the task description page.

## General Setup

Client side, we use `sendLiveUpdate()` to send messages and implement `onLiveUpdate` to handle incoming messages.

On the server side, this looks a bit different. We continuously poll the agents `get_live_update()` function
that looks if the client sent a new live update. If so, we pass this update to a handler function.
Mephisto only provides the `observe` method to send data back to the client.

**Both** `get_live_update()` and `observer()` trigger the update state method in
`agent state`. In here, we just ignore all 'communication' packages and only save
state for the pseudo submit packages.

## Protocol

Now on the concrete messages that can be sent over the web socket.

### Client to Server

Request worker statistics for the dashboard:

```json
{
  "message": "get_worker_stats"
}
```

Submit feedback:

```json
{
  "message": "set_feedback",
  "feedback": "<feedback"
}
```

Pseudo submit cad:

```json
{
  "message": "set_cad",
  "cad": "<cad>"
}
```

Pseudo submit ranking:

```json
{
  "message": "set_permutation",
  "permutation": "<permutation>"
}
```

### Server to Client

```json
{
  "message": "set_worker_stats",
  "stats": {
    "num_cads": "...",
    "num_rankings": "...",
    "num_first_place": "..."
  }
}