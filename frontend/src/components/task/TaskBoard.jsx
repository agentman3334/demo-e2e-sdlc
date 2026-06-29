import { useState, useEffect } from 'react';
import { Row, Col, Card, Tag, Avatar, Typography, Button, Empty, Spin, message } from 'antd';
import { UserOutlined, PlusOutlined } from '@ant-design/icons';
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
      setTasks(data);
    } catch {
      message.error('Failed to load tasks');
    } finally {
      setLoading(false);
    }
  };

  const fetchProjects = async () => {
    try {
      const { data } = await projectApi.list();
      setProjects(data);
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

  const handleStatusChange = async (taskId, newStatus) => {
    try {
      await taskApi.updateStatus(taskId, { status: newStatus });
      setTasks((prev) =>
        prev.map((t) => (t.id === taskId ? { ...t, status: newStatus } : t))
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

      <Row gutter={16}>
        {Object.entries(TASK_STATUSES).map(([key, col]) => (
          <Col span={6} key={key}>
            <div style={{ marginBottom: 8 }}>
              <Tag color={col.color} style={{ fontSize: 14, padding: '4px 12px' }}>
                {col.label}
              </Tag>
              <span style={{ color: '#999' }}>{tasks.filter((t) => t.status === key).length}</span>
            </div>
            <div
              style={{ minHeight: 400, padding: 8, background: '#fafafa', borderRadius: 8 }}
              onDragOver={(e) => e.preventDefault()}
              onDrop={(e) => {
                const taskId = e.dataTransfer.getData('taskId');
                handleStatusChange(taskId, key);
              }}
            >
              {tasks
                .filter((t) => t.status === key)
                .map((task) => (
                  <Card
                    key={task.id}
                    size="small"
                    draggable
                    onDragStart={(e) => e.dataTransfer.setData('taskId', task.id)}
                    style={{ marginBottom: 8, cursor: 'grab' }}
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
                ))}
            </div>
          </Col>
        ))}
      </Row>

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