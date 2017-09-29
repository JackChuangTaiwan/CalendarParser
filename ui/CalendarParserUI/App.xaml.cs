using System;
using System.Windows;
using System.Diagnostics;
using System.IO;

namespace CalendarParserUI
{
    /// <summary>
    /// App.xaml 的互動邏輯
    /// </summary>
    public partial class App : Application
    {
        public App() : base()
        {
            Directory.SetCurrentDirectory(AppDomain.CurrentDomain.BaseDirectory);
            AppDomain.CurrentDomain.UnhandledException += OnUnhandledExceptionThrown;
        }

        private void OnUnhandledExceptionThrown(object sender, UnhandledExceptionEventArgs e)
        {
            string err = string.Format("An unhandled exception occured: {0}", ((Exception)e.ExceptionObject).Message);
            MessageBox.Show(err, "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            MessageBox.Show(((Exception)e.ExceptionObject).StackTrace);
        }
    }
}
