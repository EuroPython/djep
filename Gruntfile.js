module.exports = function(grunt) {
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        compass: {
            options: {
                sassDir: 'pyconde/skins/ep14/static/assets/sass',
                cssDir: 'pyconde/skins/ep14/static/assets/css',
                imagesDir: 'pyconde/skins/ep14/static/assets/images'
            },
            server: {},
            dist: {
                options: {
                    outputStyle: 'compressed'
                }
            }
        },
        copy: {
            dist: {
                files: [
                    {
                        expand: true,
                        cwd: 'pyconde/skins/ep14/static',
                        src: [
                            'assets/images/*.png',
                            'assets/images/*.svg',
                            'assets/css/*',
                            'index.html'
                        ],
                        dest: 'dist'
                    }
                ]
            }
        },
        clean: {
            dist: ['dist'],
            compass: ['pyconde/skins/ep14/static/assets/css/*']
        },
        connect: {
            livereload: {
                options: {
                    open: true
                }
            },
            options: {
                port: 9000,
                base: "pyconde/skins/ep14/static",
                livereload: 35729
            }
        },
        rev: {
            dist: {
                src: ['dist/assets/css/*.css', 'dist/assets/images/*.png', 'dist/assets/images/*.svg']
            }
        },
        usemin: {
            html: 'dist/index.html',
            css: ['dist/assets/css/*.css']
        },
        watch: {
            compass: {
                files: ['pyconde/skins/ep14/static/assets/sass/*.scss'],
                tasks: ['compass:server']
            },
            livereload: {
                options: {
                    livereload: '<%= connect.options.livereload %>'
                },
                files: [
                    'pyconde/skins/ep14/static/assets/css/*.css',
                    'pyconde/skins/ep14/static/assets/images/*',
                    'pyconde/skins/ep14/static/index.html'
                ]
            }
        },
        concurrent: {
            server: ['compass:server']
        }
    });

    grunt.loadNpmTasks('grunt-contrib-compass');
    grunt.loadNpmTasks('grunt-contrib-connect');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-concurrent');
    grunt.loadNpmTasks('grunt-contrib-copy');
    grunt.loadNpmTasks('grunt-contrib-clean');
    grunt.loadNpmTasks('grunt-usemin');
    grunt.loadNpmTasks('grunt-rev');

    grunt.registerTask('default', ['server']);

    grunt.registerTask('server', function(target) {
        grunt.task.run([
            'clean',
            'concurrent:server',
            'connect:livereload',
            'watch'
        ]);
    });

    grunt.registerTask('dist', function(target) {
        grunt.task.run([
            'clean',
            'compass:dist',
            'copy:dist',
            'rev:dist',
            'usemin'
        ]);
    });
};