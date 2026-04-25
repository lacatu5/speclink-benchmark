const STATUS_OPTIONS = ["pending", "in_progress", "completed", "cancelled"];

export function TaskList({ tasks, onStatusChange, onDelete }) {
  if (tasks.length === 0) {
    return <p>No tasks yet.</p>;
  }

  return (
    <ul className="task-list">
      {tasks.map((task) => (
        <li key={task.id} className={`task task-${task.status}`}>
          <div className="task-header">
            <strong>#{task.id}</strong> - {task.title}
            <span className="priority">P{task.priority}</span>
          </div>
          {task.description && <p className="description">{task.description}</p>}
          <div className="task-actions">
            <select
              value={task.status}
              onChange={(e) => onStatusChange(task.id, e.target.value)}
            >
              {STATUS_OPTIONS.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
            <button onClick={() => onDelete(task.id)}>Delete</button>
          </div>
        </li>
      ))}
    </ul>
  );
}
