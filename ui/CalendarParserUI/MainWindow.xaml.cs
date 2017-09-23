using System;
using System.Windows;
using System.Windows.Input;
using System.Windows.Media;
using System.IO;
using System.Diagnostics;
using System.Threading;
using winForm = System.Windows.Forms;

namespace CalendarParserUI
{
    public partial class MainWindow : Window
    {
        private SolidColorBrush io_dragEnter = new SolidColorBrush(Color.FromArgb(0xFF, 0x5F, 0x5F, 0x5F));
        private SolidColorBrush io_dragLeave = new SolidColorBrush(Colors.Transparent);
        private Process pyProc;
        private Thread workerThread;
        private string errorMsg = "";

        public MainWindow()
        {
            InitializeComponent();
            InitializeControl();
        }

        private void InitializeControl()
        {
            tbInput.Text = "Please drag a xlsx file into here, or click here to select a file.";
        }

        private void dpHeader_MouseMove(object sender, System.Windows.Input.MouseEventArgs e)
        {
            if (e.LeftButton == MouseButtonState.Pressed)
            {
                this.DragMove();
            }
        }

        #region button control
        private void btnExit_Click(object sender, RoutedEventArgs e)
        {
            Application.Current.Shutdown();
        }

        private void btnOutput_Click(object sender, RoutedEventArgs e)
        {
            winForm.FolderBrowserDialog fbd = new winForm.FolderBrowserDialog();
            if (fbd.ShowDialog() == winForm.DialogResult.OK)
            {
                tbOutputFolder.Text = fbd.SelectedPath;
            }
        }

        private void btnInput_Click(object sender, RoutedEventArgs e)
        {
            winForm.OpenFileDialog ofd = new winForm.OpenFileDialog();
            ofd.Filter = "Excel file(*.xlsx)|*.xlsx";
            if (ofd.ShowDialog() == winForm.DialogResult.OK)
            {
                ChangeImageOfInputRegion(true, ofd.FileName);
            }
        }

        private void btnInput_DragEnter(object sender, DragEventArgs e)
        {
            if (e.Data.GetDataPresent(DataFormats.FileDrop))
                e.Effects = DragDropEffects.Copy;
        }

        private void btnInput_Drop(object sender, DragEventArgs e)
        {
            if (e.Data.GetDataPresent(DataFormats.FileDrop))
            {
                Console.WriteLine("file dropped");
                string[] files = (string[])e.Data.GetData(DataFormats.FileDrop);
                string firstFile = files[0];
                if (Path.GetExtension(firstFile) != ".xlsx")
                {
                    return;
                }
                ChangeImageOfInputRegion(true, firstFile);
            }
        }

        private void btnAppSetting_Click(object sender, RoutedEventArgs e)
        {
            Window winSetting = new WindowSetting();
            winSetting.Owner = this;
            winSetting.WindowStartupLocation = WindowStartupLocation.CenterOwner;
            winSetting.Show();
        }

        private void btnConvert_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                if (!File.Exists(tbInput.Text) || !Directory.Exists(tbOutputFolder.Text))
                    return;
                string ifile = tbInput.Text;
                string ofile = tbOutputFolder.Text;
                workerThread = new Thread(() => Convert(ifile, ofile));
                workerThread.Start();
                workerThread.Join();

                if (!string.IsNullOrEmpty(errorMsg))
                    winForm.MessageBox.Show(errorMsg);
                tbStatus.Text = string.Format("{0}: File is converted sucessfully.", DateTime.Now);
            }
            catch (Exception ex)
            {
                winForm.MessageBox.Show(ex.Message);
            }
        }
        #endregion

        private void ChangeImageOfInputRegion(bool isFileDropped, string fileName)
        {
            if (isFileDropped)
            {
                imgInputFile.Visibility = Visibility.Visible;
                imgInputRegion.Visibility = Visibility.Hidden;
                tbInput.Text = fileName;
                tbInput.Foreground = new SolidColorBrush(Color.FromArgb(0xFF, 0x20, 0x20, 0x20));
            }
        }

        #region python shell setting
        private void checkPyShell()
        {
            if (pyProc == null)
            {
                if (!File.Exists(Properties.Settings.Default.PythonPath) || 
                    !File.Exists(Properties.Settings.Default.ScriptPath))
                {
                    throw new Exception("Invalid Python path or Script path, please reset them in setting.");
                }

                pyProc = new Process();
                pyProc.StartInfo.FileName = Properties.Settings.Default.PythonPath;
                pyProc.StartInfo.WorkingDirectory = Path.GetDirectoryName(Properties.Settings.Default.ScriptPath);
                pyProc.StartInfo.CreateNoWindow = true;
                pyProc.StartInfo.UseShellExecute = false;
                pyProc.StartInfo.RedirectStandardOutput = true;
                pyProc.StartInfo.RedirectStandardError = true;
                pyProc.StartInfo.WindowStyle = ProcessWindowStyle.Hidden;
                pyProc.StartInfo.Arguments += string.Format("{0}", Properties.Settings.Default.ScriptPath);
            }
            else
            {
                pyProc.StartInfo.Arguments = string.Format("{0}", Properties.Settings.Default.ScriptPath);
            }
        }
        #endregion

        private void Convert(string ifile, string odir)
        {
            checkPyShell();
            pyProc.StartInfo.Arguments += PyArgs.InputFile + ifile;
            pyProc.StartInfo.Arguments += PyArgs.OutputDir + odir;

            try
            {
                pyProc.Start();
                errorMsg = pyProc.StandardError.ReadToEnd();
                pyProc.WaitForExit();
            }
            catch (Exception ex)
            {
                throw ex;
            }
        }
    }
}
