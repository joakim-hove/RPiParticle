import os
import requests
import shutil
import json
import tempfile 
from unittest import TestCase, skipUnless
import os.path
import stat

from device_config import DeviceConfig
from context import TestContext
        

try:
    response = requests.get("https://github.com")
    network = True
except Exception:
    network = False


class DeviceConfigTest(TestCase):

    def setUp(self):
        fd , self.config_file = tempfile.mkstemp( )
        os.close(fd)

        self.tmpdir = tempfile.mkdtemp( )
        self.context = TestContext( )

    def tearDown(self):
        if os.path.isfile( self.config_file ):
            os.unlink( self.config_file )

        if os.path.isdir( self.tmpdir ):
            shutil.rmtree( self.tmpdir )



    def test_create(self):
        with self.assertRaises(IOError):
            config = DeviceConfig("file/not/found")
        
        with open(self.config_file , "w") as f:
            f.write("No - not valid JSON")

        with self.assertRaises(ValueError):
            deviceconfig = DeviceConfig(self.config_file)
        
        conf = {"key" : "value"}
        with open(self.config_file , "w") as f:
            f.write(json.dumps( conf ))

        with self.assertRaises(KeyError):
            config = DeviceConfig(self.config_file)

        conf_no_key = {"git_follow" : True, "git_repo" : "github" , "git_ref" : "master" , "sensor_list" : ["A","B","C"] , 
                       "post_path" : "XYZ" , "server_url" : "http:???" , "config_path" : "xyz" , "device_id" : "dev0"}
        with open(self.config_file , "w") as f:
            f.write(json.dumps( conf_no_key ))

        with self.assertRaises(KeyError):        
            config = DeviceConfig( self.config_file )

        config = DeviceConfig( self.config_file , post_key = "Key")
            
        conf = {"git_follow" : True, "git_repo" : "github" , "git_ref" : "master" , "sensor_list" : ["A","B","C"] , "post_key" : "Key",
                "post_path" : "XYZ" , "server_url" : "http:???" , "config_path" : "xyz" , "device_id" : "dev0"}
        with open(self.config_file , "w") as f:
            f.write(json.dumps( conf ))
        
        config = DeviceConfig( self.config_file )
        config_file2 = os.path.join( self.tmpdir , "config2")
        config.save( filename = config_file2 )
        self.assertEqual( config.getServerURL( ) , "http:???")
        self.assertEqual( config.getDeviceID( ) , "dev0")

        config2 = DeviceConfig( config_file2 )
        os.unlink( config_file2 )
        config2.save( )
        self.assertTrue( os.path.isfile( config_file2 ) )

        self.assertTrue( "github" , config2.getRepoURL( ) )

        with open("conf","w") as f:
            f.write(json.dumps( conf ))

        conf2 = {"git_follow" : True , "git_repo" : "github" , "git_ref" : "master" , "sensor_list" : ["A","B","C"] , "post_key" : "KeyX",
                "post_path" : "XYZ" , "server_url" : "http:???" , "config_path" : "xyz" , "device_id" : "dev0"}

        with open("conf2","w") as f:
            f.write(json.dumps( conf2 ))


        c1 = DeviceConfig( "conf" )
        c2 = DeviceConfig( "conf" )
        
        self.assertEqual( c1 , c2 )
        self.assertFalse( c1 != c2 )

        c2 = DeviceConfig( "conf2" )
        self.assertFalse( c1 == c2 )
        self.assertTrue( c1 != c2 )

        c1.data["git_follow"] = True
        self.assertTrue( c1.updateRequired( ) )

        
    @skipUnless(network, "Requires network access")
    def test_url_get(self):
        with self.assertRaises(requests.ConnectionError):
            deviceconfig = DeviceConfig.download( "http://does/not/exist")

        # The post_key supplied here is not valid for anything, but we pass the "must have post_key test".
        deviceconfig = DeviceConfig.download( "https://friskby.herokuapp.com/sensor/api/device/FriskPITest/" , post_key = "xxx")
        deviceconfig.save( filename = self.config_file )


    @skipUnless(network, "Requires network access")
    def test_post_msg(self):
        status = self.context.device_config.logMessage( "Testing" )
        self.assertEqual( status ,  201 )

