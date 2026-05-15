import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { AppLayout } from '@/widgets/layout';
import { HomePage } from '@/pages/home';
import { ProfilePage } from '@/pages/profile';
import { SettingsPage } from '@/pages/settings';
import { LoginPage } from '@/pages/login';
import { ProtectedRoute } from '@/shared/ui/protected-route';

const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    element: <AppLayout />,
    children: [
      {
        path: '/',
        element: (
          <ProtectedRoute>
            <HomePage />
          </ProtectedRoute>
        ),
      },
      {
        path: '/profile',
        element: (
          <ProtectedRoute>
            <ProfilePage />
          </ProtectedRoute>
        ),
      },
      {
        path: '/settings',
        element: (
          <ProtectedRoute>
            <SettingsPage />
          </ProtectedRoute>
        ),
      },
    ],
  },
]);

export function AppRouter() {
  return <RouterProvider router={router} />;
}
