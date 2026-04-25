import { useEffect, useState } from "react";
import { useTasks } from "../hooks/useTasks";
import { TaskList } from "./TaskList";

export function Dashboard({ onLogout }) {
  const { tasks, stats, loading, error, addTask, changeStatus, remove, loadStats } = useTasks();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState(1);

  useEffect(() => {
    loadStats();
  }, [loadStats, tasks.length]);

  const handleAdd = async (e) => {
    e.preventDefault();
    await addTask(title, description, priority);
    setTitle("");
    setDescription("");
    setPriority(1);
  };

  return (
    <div>
      <header>
        <h1>Task Manager</h1>
        <button onClick={onLogout}>Logout</button>
      </header>

      {stats && (
        <div className="stats">
          <span>Total: {stats.total}</span>
          <span>Pending: {stats.pending}</span>
          <span>In Progress: {stats.in_progress}</span>
          <span>Completed: {stats.completed}</span>
          <span>Cancelled: {stats.cancelled}</span>
        </div>
      )}

      <form onSubmit={handleAdd}>
        <input placeholder="Title" value={title} onChange={(e) => setTitle(e.target.value)} required />
        <input placeholder="Description" value={description} onChange={(e) => setDescription(e.target.value)} />
        <select value={priority} onChange={(e) => setPriority(Number(e.target.value))}>
          <option value={1}>Low</option>
          <option value={2}>Medium</option>
          <option value={3}>High</option>
        </select>
        <button type="submit">Add Task</button>
      </form>

      {error && <div className="error">{error}</div>}
      {loading ? <p>Loading...</p> : <TaskList tasks={tasks} onStatusChange={changeStatus} onDelete={remove} />}
    </div>
  );
}
