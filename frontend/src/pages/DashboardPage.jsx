import { useEffect, useState } from 'react';
import { Row, Col, Card, Statistic, Typography, Progress, Spin, Select, Tag } from 'antd';
import {
  CheckCircleOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined,
  ProjectOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import analyticsApi from '../api/analyticsApi';

function SimpleDonut({ data, colors }) {
  const total = data.reduce((sum, d) => sum + d.value, 0);
  if (total === 0) return <Typography.Text type="secondary">No data</Typography.Text>;

  let cumulative = 0;
  const segments = data.map((d, i) => {
    const start = (cumulative / total) * 360;
    cumulative += d.value;
    const end = (cumulative / total) * 360;
    return { ...d, start, end, color: colors[i % colors.length] };
  });

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
      <div style={{ position: 'relative', width: 160, height: 160 }}>
        <svg viewBox="0 0 36 36" style={{ transform: 'rotate(-90deg)' }}>
          {segments.map((s, i) => (
            <circle
              key={i}
              r="15.91549"
              cx="18"
              cy="18"
              fill="transparent"
              stroke={s.color}
              strokeWidth="3.5"
              strokeDasharray={`${((s.end - s.start) / 360) * 100} ${100 - ((s.end - s.start) / 360) * 100}`}
              strokeDashoffset={`${-((s.start / 360) * 100)}`}
            />
          ))}
        </svg>
        <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', textAlign: 'center' }}>
          <Typography.Text strong style={{ fontSize: 20 }}>{total}</Typography.Text>
          <br />
          <Typography.Text type="secondary" style={{ fontSize: 11 }}>tasks</Typography.Text>
        </div>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        {segments.map((s, i) => (
          <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <div style={{ width: 10, height: 10, borderRadius: 2, background: s.color }} />
            <Typography.Text style={{ fontSize: 12 }}>{s.type}: {s.value}</Typography.Text>
          </div>
        ))}
      </div>
    </div>
  );
}

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

  const todoCount = (stats?.total_tasks || 0) - (stats?.completed || 0) - (stats?.in_progress || 0);
  const statusData = [
    { type: 'To Do', value: todoCount > 0 ? todoCount : 0 },
    { type: 'In Progress', value: stats?.in_progress || 0 },
    { type: 'Completed', value: stats?.completed || 0 },
  ].filter(d => d.value > 0);

  const projectStatusData = projectStats ? [
    { type: 'To Do', value: projectStats.status_counts?.todo || 0 },
    { type: 'In Progress', value: projectStats.status_counts?.in_progress || 0 },
    { type: 'In Review', value: projectStats.status_counts?.in_review || 0 },
    { type: 'Done', value: projectStats.status_counts?.done || 0 },
  ].filter(d => d.value > 0) : [];

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
            <SimpleDonut data={statusData} colors={['#d9d9d9', '#1677ff', '#52c41a']} />
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
                <SimpleDonut data={projectStatusData} colors={['#d9d9d9', '#1677ff', '#faad14', '#52c41a']} />
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
