import { useEffect, useState } from 'react';
import { Row, Col, Card, Statistic, Typography, Progress, Spin, Select } from 'antd';
import {
  CheckCircleOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined,
  ProjectOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { Pie } from '@ant-design/charts';
import analyticsApi from '../api/analyticsApi';

export default function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [projectStats, setProjectStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    analyticsApi.getDashboard()
      .then(({ data }) => setStats(data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const fetchProjectStats = async (projectId) => {
    try {
      const { data } = await analyticsApi.getProjectStats(projectId);
      setProjectStats(data);
    } catch {
      setProjectStats(null);
    }
  };

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;

  const statusPieData = stats ? [
    { type: 'To Do', value: (stats.total_tasks || 0) - (stats.completed || 0) - (stats.in_progress || 0) },
    { type: 'In Progress', value: stats.in_progress || 0 },
    { type: 'Completed', value: stats.completed || 0 },
  ].filter(d => d.value > 0) : [];

  const pieConfig = {
    appendPadding: 10,
    data: statusPieData,
    angleField: 'value',
    colorField: 'type',
    radius: 0.8,
    label: {
      type: 'outer',
      content: '{name} {percentage}',
    },
    interactions: [{ type: 'pie-legend-active' }, { type: 'element-active' }],
    color: ['#d9d9d9', '#1677ff', '#52c41a'],
  };

  const projectPieData = projectStats ? [
    { type: 'To Do', value: projectStats.status_counts?.todo || 0 },
    { type: 'In Progress', value: projectStats.status_counts?.in_progress || 0 },
    { type: 'In Review', value: projectStats.status_counts?.in_review || 0 },
    { type: 'Done', value: projectStats.status_counts?.done || 0 },
  ].filter(d => d.value > 0) : [];

  const projectPieConfig = {
    appendPadding: 10,
    data: projectPieData,
    angleField: 'value',
    colorField: 'type',
    radius: 0.8,
    label: {
      type: 'outer',
      content: '{name} {percentage}',
    },
    interactions: [{ type: 'pie-legend-active' }, { type: 'element-active' }],
    color: ['#d9d9d9', '#1677ff', '#faad14', '#52c41a'],
  };

  return (
    <div>
      <Typography.Title level={3} style={{ marginBottom: 24 }}>Dashboard</Typography.Title>
      <Row gutter={16} style={{ marginBottom: 32 }}>
        <Col span={6}>
          <Card>
            <Statistic title="Total Tasks" value={stats?.total_tasks || 0} prefix={<ProjectOutlined />} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="Completed" value={stats?.completed || 0} prefix={<CheckCircleOutlined />} valueStyle={{ color: '#3f8600' }} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="In Progress" value={stats?.in_progress || 0} prefix={<ClockCircleOutlined />} valueStyle={{ color: '#1890ff' }} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="Overdue" value={stats?.overdue || 0} prefix={<ExclamationCircleOutlined />} valueStyle={{ color: '#cf1322' }} />
          </Card>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginBottom: 32 }}>
        <Col span={12}>
          <Card title="Task Distribution">
            {statusPieData.length > 0 ? <Pie {...pieConfig} /> : <Typography.Text type="secondary">No tasks yet</Typography.Text>}
          </Card>
        </Col>
        <Col span={12}>
          <Card title="Project Progress" extra={
            <Select
              placeholder="Select project"
              style={{ width: 180 }}
              onChange={fetchProjectStats}
              options={(stats?.projects || []).map((p) => ({ label: p.name, value: p.id }))}
            />
          }>
            {projectStats ? (
              <div>
                <div style={{ marginBottom: 16 }}>
                  <Typography.Text strong>{projectStats.project_name}</Typography.Text>
                  <Progress percent={projectStats.progress} style={{ marginTop: 8 }} />
                </div>
                {projectPieData.length > 0 && <Pie {...projectPieConfig} />}
              </div>
            ) : (
              <Typography.Text type="secondary">Select a project to view details</Typography.Text>
            )}
          </Card>
        </Col>
      </Row>

      <Typography.Title level={4} style={{ marginBottom: 16 }}>Projects</Typography.Title>
      <Row gutter={[16, 16]}>
        {(stats?.projects || []).map((project) => (
          <Col xs={24} sm={12} lg={8} key={project.id}>
            <Card hoverable onClick={() => navigate(`/projects/${project.id}`)}>
              <Typography.Text strong>{project.name}</Typography.Text>
              <Progress percent={project.progress} style={{ marginTop: 8 }} />
            </Card>
          </Col>
        ))}
      </Row>
    </div>
  );
}
