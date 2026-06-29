import { useState, useEffect } from 'react';
import { Row, Col, Button, Typography, Spin, Empty } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import ProjectCard from '../../components/project/ProjectCard';
import ProjectForm from '../../components/project/ProjectForm';
import projectApi from '../../api/projectApi';
import analyticsApi from '../../api/analyticsApi';
import { message } from 'antd';

export default function ProjectsPage() {
  const [projects, setProjects] = useState([]);
  const [progressMap, setProgressMap] = useState({});
  const [loading, setLoading] = useState(true);
  const [formOpen, setFormOpen] = useState(false);

  const fetchProjects = async () => {
    try {
      const { data } = await projectApi.list();
      setProjects(data);
    } catch (error) {
      message.error('Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  const fetchProgress = async () => {
    try {
      const { data } = await analyticsApi.getDashboard();
      const map = {};
      (data.projects || []).forEach((p) => { map[p.id] = p.progress; });
      setProgressMap(map);
    } catch {
      // silently fail
    }
  };

  useEffect(() => {
    fetchProjects();
    fetchProgress();
  }, []);

  const handleCreate = async (values) => {
    try {
      await projectApi.create(values);
      message.success('Project created');
      fetchProjects();
    } catch (error) {
      message.error(error.response?.data?.detail || 'Failed to create project');
    }
  };

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <Typography.Title level={3} style={{ margin: 0 }}>Projects</Typography.Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setFormOpen(true)}>
          New Project
        </Button>
      </div>
      {projects.length === 0 ? (
        <Empty description="No projects yet. Create one to get started!" />
      ) : (
        <Row gutter={[16, 16]}>
          {projects.map((project) => (
            <Col xs={24} sm={12} lg={8} key={project.id}>
              <ProjectCard project={project} progress={progressMap[project.id] || 0} />
            </Col>
          ))}
        </Row>
      )}
      <ProjectForm open={formOpen} onClose={() => setFormOpen(false)} onSubmit={handleCreate} />
    </div>
  );
}