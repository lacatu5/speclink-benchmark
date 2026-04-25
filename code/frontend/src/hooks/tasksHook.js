import { useState, useCallback, useEffect } from "react";
import * as api from "../api/client";

export function useTasks(initialStatus = null) {
  const [tasks, setTasks] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const refresh = useCallback(async (status = null) => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.listTasks(status);
      setTasks(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const loadStats = useCallback(async () => {
    try {
      const data = await api.getTaskStats();
      setStats(data);
    } catch (err) {
      setError(err.message);
    }
  }, []);

  const addTask = useCallback(async (title, description, priority) => {
    const task = await api.createTask(title, description, priority);
    setTasks((prev) => [task, ...prev]);
    return task;
  }, []);

  const changeStatus = useCallback(async (taskId, status) => {
    const updated = await api.updateTaskStatus(taskId, status);
    setTasks((prev) => prev.map((t) => (t.id === taskId ? updated : t)));
    return updated;
  }, []);

  const remove = useCallback(async (taskId) => {
    await api.deleteTask(taskId);
    setTasks((prev) => prev.filter((t) => t.id !== taskId));
  }, []);

  useEffect(() => {
    refresh(initialStatus);
  }, [refresh, initialStatus]);

  return { tasks, stats, loading, error, refresh, loadStats, addTask, changeStatus, remove };
}
