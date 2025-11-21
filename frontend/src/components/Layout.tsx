import { Layout as AntLayout, Menu, Typography } from 'antd';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  HomeOutlined,
  TeamOutlined,
  SettingOutlined,
  SolutionOutlined,
} from '@ant-design/icons';
import logo from '../assets/logo.svg';

const { Header, Content, Sider } = AntLayout;
const { Title, Text } = Typography;

// 릴리즈 날짜
const RELEASE_DATE = '2025-11-21';

export const Layout = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: '홈',
    },
    {
      key: '/students',
      icon: <TeamOutlined />,
      label: '학생 관리',
    },
    {
      key: '/rules',
      icon: <SettingOutlined />,
      label: '규칙 설정',
    },
    {
      key: '/assignments',
      icon: <SolutionOutlined />,
      label: '반편성',
    },
  ];

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Header style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: '#001529',
        padding: '0 24px',
        gap: '16px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <img src={logo} alt="AI 반편성 시스템" style={{ height: '48px', width: '48px' }} />
          <Title level={3} style={{ color: 'white', margin: 0 }}>
            AI 반편성 시스템 v0.1.0
          </Title>
        </div>
        <Text style={{ color: '#8c8c8c', fontSize: '14px' }}>
          릴리즈: {RELEASE_DATE}
        </Text>
      </Header>
      <AntLayout>
        <Sider width={200} style={{ background: '#fff' }}>
          <Menu
            mode="inline"
            selectedKeys={[location.pathname]}
            items={menuItems}
            onClick={({ key }) => navigate(key)}
            style={{ height: '100%', borderRight: 0 }}
          />
        </Sider>
        <AntLayout style={{ padding: '24px' }}>
          <Content
            style={{
              background: '#fff',
              padding: 24,
              margin: 0,
              minHeight: 280,
            }}
          >
            <Outlet />
          </Content>
        </AntLayout>
      </AntLayout>
    </AntLayout>
  );
};

