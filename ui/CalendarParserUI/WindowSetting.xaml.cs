using System.Windows;
using System.Windows.Input;
using System.IO;
using winForm = System.Windows.Forms;

namespace CalendarParserUI
{
    public partial class WindowSetting : Window
    {
        public WindowSetting()
        {
            InitializeComponent();
            InitializeControl();
        }

        private void InitializeControl()
        {
            txtPythonPath.Text = Properties.Settings.Default.PythonPath;
            txtScriptPath.Text = Properties.Settings.Default.ScriptPath;
        }

        private void DockPanel_MouseMove(object sender, MouseEventArgs e)
        {
            if (e.LeftButton == MouseButtonState.Pressed)
            {
                this.DragMove();
            }
        }

        private void btnCancel_Click(object sender, RoutedEventArgs e)
        {
            this.Close();
        }

        private void Grid_MouseDown(object sender, MouseButtonEventArgs e)
        {
            if (e.LeftButton == MouseButtonState.Pressed)
            {
                this.DragMove();
            }
        }

        private void btnSelectPython_Click(object sender, RoutedEventArgs e)
        {
            winForm.OpenFileDialog ofd = new winForm.OpenFileDialog();
            if (ofd.ShowDialog() == winForm.DialogResult.OK)
            {
                if (File.Exists(ofd.FileName))
                    txtPythonPath.Text = ofd.FileName;
            }
        }

        private void btnSelectScript_Click(object sender, RoutedEventArgs e)
        {
            winForm.OpenFileDialog ofd = new winForm.OpenFileDialog();
            if (ofd.ShowDialog() == winForm.DialogResult.OK)
            {
                if (File.Exists(ofd.FileName))
                    txtScriptPath.Text = ofd.FileName;
            }
        }

        private void btnSave_Click(object sender, RoutedEventArgs e)
        {
            Properties.Settings.Default.PythonPath = txtPythonPath.Text;
            Properties.Settings.Default.ScriptPath = txtScriptPath.Text;
            Properties.Settings.Default.Save();
            this.Close();
        }
    }
}
