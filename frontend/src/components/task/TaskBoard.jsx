import { useState, useEffect } from 'react';
import { Card, Tag, Avatar, Typography, Button, Empty, Spin, message } from 'antd';
import { UserOutlined, PlusOutlined } from '@ant-design/icons';
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';
import taskApi from '../../api/taskApi';
import projectApi from '../../api/projectApi';
import TaskForm from './TaskForm';
import { TASK_STATUSES, PRIORITY_COLORS } from '../../utils/constants';

export default function TaskBoard({ projectId }) {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [formOpen, setFormOpen] = useState(false);
  const [projects, setProjects] = useState([]);
  const [selectedProjectId, setSelectedProjectId] = useState(projectId);

  const fetchTasks = async () => {
    setLoading(true);
    try {
      const params = {};
      if (selectedProjectId) params.project_id = selectedProjectId;
      const { data } = await taskApi.list(params);
      setTasks(data.items || data);
    } catch {
      message.error('Failed to load tasks');
    } finally {
      setLoading(false);
    }
  };

  const fetchProjects = async () => {
    try {
      const { data } = await projectApi.list();
      setProjects(data.items || data);
    } catch {
      // silently fail
    }
  };

  useEffect(() => {
    fetchTasks();
  }, [selectedProjectId]);

  useEffect(() => {
    if (!projectId) fetchProjects();
  }, [projectId]);

  const handleDragEnd = async (result) => {
    const { draggableId, destination } = result;
    if (!destination) return;
    const newStatus = destination.droppableId;
    try {
      await taskApi.updateStatus(draggableId, { status: newStatus });
      setTasks((prev) =>
        prev.map((t) => (t.id === draggableId ? { ...t, status: newStatus } : t))
      );
    } catch {
      message.error('Failed to update task status');
    }
  };

  const handleCreateTask = async (values) => {
    try {
      const pid = values.project_id || selectedProjectId;
      await taskApi.create(pid, values);
      message.success('Task created');
      fetchTasks();
    } catch (error) {
      message.error(error.response?.data?.detail || 'Failed to create task');
    }
  };

  const handleDeleteTask = async (taskId) => {
    try {
      await taskApi.delete(taskId);
      message.success('Task deleted');
      setTasks((prev) => prev.filter((t) => t.id !== taskId));
    } catch {
      message.error('Failed to delete task');
    }
  };

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '40px auto' }} />;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div style={{ display: 'flex', gap: 8 }}>
          <Button
            type={!selectedProjectId ? 'primary' : 'default'}
            onClick={() => setSelectedProjectId(null)}
          >
            All
          </Button>
          {projects.map((p) => (
            <Button
              key={p.id}
              type={selectedProjectId === p.id ? 'primary' : 'default'}
              onClick={() => setSelectedProjectId(p.id)}
            >
              {p.name}
            </Button>
          ))}
        </div>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setFormOpen(true)}>
          New Task
        </Button>
      </div>

      <DragDropContext onDragEnd={handleDragEnd}>
        <div style={{ display: 'flex', gap: 12, overflowX: 'auto' }}>
          {Object.entries(TASK_STATUSES).map(([key, col]) => {
            const columnTasks = tasks.filter((t) => t.status === key);
            return (
              <div key={key} style={{ flex: '1 1 0%', minWidth: 260 }}>
                <div style={{ marginBottom: 8, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Tag color={col.color} style={{ fontSize: 14, padding: '4px 12px' }}>
                    {col.label}
                  </Tag>
                  <span style={{ color: '#999' }}>{columnTasks.length}</span>
                </div>
                <Droppable droppableId={key}>
                  {(provided, snapshot) => (
                    <div
                      ref={provided.innerRef}
                      {...provided.droppableProps}
                      style={{
                        minHeight: 400,
                        padding: 8,
                        background: snapshot.isDraggingOver ? '#e6f4ff' : '#fafafa',
                        borderRadius: 8,
                        transition: 'background 0.2s ease',
                      }}
                    >
                      {columnTasks.map((task, index) => (
                        <Draggable key={task.id} draggableId={task.id} index={index}>
                          {(provided, snapshot) => (
                            <div
                              ref={provided.innerRef}
                              {...provided.draggableProps}
                              {...provided.dragHandleProps}
                              style={{
                                ...provided.draggableProps.style,
                                marginBottom: 8,
                              }}
                            >
                              <Card
                                size="small"
                                style={{
                                  cursor: 'grab',
                                  opacity: snapshot.isDragging ? 0.8 : 1,
                                  borderLeft: `3px solid ${PRIORITY_COLORS[task.priority] === 'red' ? '#ff4d4f' : PRIORITY_COLORS[task.priority] === 'orange' ? '#fa8c16' : PRIORITY_COLORS[task.priority] === 'magenta' ? '#eb2f96' : '#1677ff'}`,
                                }}
                              >
                                <Typography.Text strong>{task.title}</Typography.Text>
                                {task.description && (
                                  <Typography.Paragraph type="secondary" ellipsis={{ rows: 2 }} style={{ marginTop: 4, marginBottom: 0, fontSize: 12 }}>
                                    {task.description}
                                  </Typography.Paragraph>
                                )}
                                <div style={{ marginTop: 8, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                  <Tag color={PRIORITY_COLORS[task.priority]}>{task.priority}</Tag>
                                  {task.assignee_id && (
                                    <Avatar size="small" icon={<UserOutlined />} style={{ backgroundColor: '#1677ff' }} />
                                  )}
                                </div>
                              </Card>
                            </div>
                          )}
                        </Draggable>
                      ))}
                      {provided.placeholder}
                    </div>
                  )}
                </Droppable>
              </div>
            );
          })}
        </div>
      </DragDropContext>

      <TaskForm
        open={formOpen}
        onClose={() => setFormOpen(false)}
        onSubmit={handleCreateTask}
        projects={projects}
        defaultProjectId={selectedProjectId}
      />
    </div>
  );
}
