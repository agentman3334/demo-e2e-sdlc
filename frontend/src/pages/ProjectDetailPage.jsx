import { useState, useEffect } from 'react';
import { Typography, Descriptions, Tag, Button, Spin, Popconfirm, message } from 'antd';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeftOutlined, DeleteOutlined, EditOutlined } from '@ant-design/icons';
import projectApi from '../api/projectApi';
import taskApi from '../api/taskApi';
import ProjectForm from '../components/project/ProjectForm';
import TaskBoard from '../components/task/TaskBoard';
import { PROJECT_STATUSES } from '../utils/constants';

export default function ProjectDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editOpen, setEditOpen] = useState(false);

  const fetchProject = async () => {
    try {
      const { data } = await projectApi.get(id);
      setProject(data);
    } catch {
      message.error('Failed to load project');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProject();
  }, [id]);

  const handleUpdate = async (values) => {
    try {
      await projectApi.update(id, values);
      message.success('Project updated');
      fetchProject();
    } catch (error) {
      message.error(error.response?.data?.detail || 'Failed to update project');
    }
  };

  const handleDelete = async () => {
    try {
      await projectApi.delete(id);
      message.success('Project deleted');
      navigate('/projects');
    } catch (error) {
      message.error('Failed to delete project');
    }
  };

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;
  if (!project) return <Typography.Text type="danger">Project not found</Typography.Text>;

  const statusInfo = PROJECT_STATUSES[project.status] || PROJECT_STATUSES.active;

  return (
    <div>
      <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/projects')} style={{ marginBottom: 16 }}>
        Back to Projects
      </Button>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <Typography.Title level={3} style={{ margin: 0 }}>{project.name}</Typography.Title>
        <div>
          <Button icon={<EditOutlined />} onClick={() => setEditOpen(true)} style={{ marginRight: 8 }}>Edit</Button>
          <Popconfirm title="Delete this project?" onConfirm={handleDelete} okText="Yes" cancelText="No">
            <Button danger icon={<DeleteOutlined />}>Delete</Button>
          </Popconfirm>
        </div>
      </div>
      <Descriptions bordered style={{ marginBottom: 24 }}>
        <Descriptions.Item label="Status"><Tag color={statusInfo.color}>{statusInfo.label}</Tag></Descriptions.Item>
        <Descriptions.Item label="Created">{new Date(project.created_at).toLocaleDateString()}</Descriptions.Item>
        <Descriptions.Item label="Updated">{new Date(project.updated_at).toLocaleDateString()}</Descriptions.Item>
      </Descriptions>
      {project.description && (
        <Typography.Paragraph style={{ marginBottom: 24 }}>{project.description}</Typography.Paragraph>
      )}
      <Typography.Title level={4}>Tasks</Typography.Title>
      <TaskBoard projectId={id} />
      <ProjectForm open={editOpen} onClose={() => setEditOpen(false)} onSubmit={handleUpdate} initialValues={project} />
    </div>
  );
}